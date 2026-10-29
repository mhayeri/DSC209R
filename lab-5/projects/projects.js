import { fetchJSON, renderProjects } from '../global.js';
import * as d3 from 'https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm';

const projects = await fetchJSON('../lib/projects.json');
const projectsContainer = document.querySelector('.projects');
const projectsTitle = document.querySelector('.projects-title');

let colors = d3.scaleOrdinal(d3.schemeTableau10);
let arcGenerator = d3.arc().innerRadius(0).outerRadius(50);
let sliceGenerator = d3.pie().value((d) => d.value);

function renderPieChart(projectsGiven) {
  let rolledData = d3.rollups(
    projectsGiven,
    (v) => v.length,
    (d) => d.year,
  );
  let data = rolledData.map(([year, count]) => ({ value: count, label: year }));
  let arcData = sliceGenerator(data);
  let arcs = arcData.map((d) => arcGenerator(d));

  let svg = d3.select('svg');
  svg.selectAll('path').remove();
  let legend = d3.select('.legend');
  legend.selectAll('li').remove();

  arcs.forEach((arc, idx) => {
    svg.append('path').attr('d', arc).attr('fill', colors(idx));
  });

  data.forEach((d, idx) => {
    legend
      .append('li')
      .attr('style', `--color:${colors(idx)}`)
      .attr('class', 'legend-item')
      .html(`<span class="swatch"></span> ${d.label} <em>(${d.value})</em>`);
  });
}

function render(projectsGiven) {
  renderProjects(projectsGiven, projectsContainer, 'h2');
  renderPieChart(projectsGiven);
  if (projectsTitle) {
    projectsTitle.textContent = `${projectsGiven.length} Projects`;
  }
}

let query = '';

function searchProjects(list) {
  return list.filter((project) => {
    let values = Object.values(project).join('
').toLowerCase();
    return values.includes(query.toLowerCase());
  });
}

render(projects);

let searchInput = document.querySelector('.searchBar');
searchInput.addEventListener('input', (event) => {
  query = event.target.value;
  render(searchProjects(projects));
});
