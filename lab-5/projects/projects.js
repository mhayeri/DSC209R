import { fetchJSON, renderProjects } from '../global.js';
import * as d3 from 'https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm';

const projects = await fetchJSON('../lib/projects.json');
const projectsContainer = document.querySelector('.projects');
const projectsTitle = document.querySelector('.projects-title');

let colors = d3.scaleOrdinal(d3.schemeTableau10);
let arcGenerator = d3.arc().innerRadius(0).outerRadius(50);
let sliceGenerator = d3.pie().value((d) => d.value);

// The search box and the pie both filter the same list, so they share state.
// The selection is stored as a year label, not an index, because the wedges
// change position when a search narrows the data.
let query = '';
let selectedYear = null;
let pieData = [];

function searchProjects(list) {
  return list.filter((project) => {
    let values = Object.values(project).join('\n').toLowerCase();
    return values.includes(query.toLowerCase());
  });
}

function visibleProjects() {
  let matches = searchProjects(projects);
  return selectedYear === null
    ? matches
    : matches.filter((project) => project.year === selectedYear);
}

function renderList() {
  let shown = visibleProjects();
  renderProjects(shown, projectsContainer, 'h2');
  if (projectsTitle) {
    projectsTitle.textContent = `${shown.length} Projects`;
  }
}

function highlightSelection() {
  let selectedIndex = pieData.findIndex((d) => d.label === selectedYear);

  d3.select('svg')
    .selectAll('path')
    .attr('class', (_, i) => (i === selectedIndex ? 'selected' : ''));
  d3.select('.legend')
    .selectAll('li')
    .attr('class', (_, i) =>
      i === selectedIndex ? 'legend-item selected' : 'legend-item',
    );
}

function selectWedge(idx) {
  let year = pieData[idx].label;
  selectedYear = selectedYear === year ? null : year;
  highlightSelection();
  renderList();
}

// The pie reflects the search results, not the year selection, so the other
// wedges stay visible and clickable while one year is selected.
function renderPieChart(projectsGiven) {
  let rolledData = d3.rollups(
    projectsGiven,
    (v) => v.length,
    (d) => d.year,
  );
  pieData = rolledData.map(([year, count]) => ({ value: count, label: year }));
  let arcs = sliceGenerator(pieData).map((d) => arcGenerator(d));

  // A selected year that the search no longer matches has no wedge to show.
  if (!pieData.some((d) => d.label === selectedYear)) {
    selectedYear = null;
  }

  let svg = d3.select('svg');
  svg.selectAll('path').remove();
  let legend = d3.select('.legend');
  legend.selectAll('li').remove();

  arcs.forEach((arc, idx) => {
    svg
      .append('path')
      .attr('d', arc)
      .attr('fill', colors(idx))
      .on('click', () => selectWedge(idx));
  });

  pieData.forEach((d, idx) => {
    legend
      .append('li')
      .attr('style', `--color:${colors(idx)}`)
      .attr('class', 'legend-item')
      .html(`<span class="swatch"></span> ${d.label} <em>(${d.value})</em>`)
      .on('click', () => selectWedge(idx));
  });

  highlightSelection();
}

renderPieChart(projects);
renderList();

let searchInput = document.querySelector('.searchBar');
searchInput.addEventListener('input', (event) => {
  query = event.target.value;
  renderPieChart(searchProjects(projects));
  renderList();
});
