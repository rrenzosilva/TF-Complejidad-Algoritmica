document.addEventListener('DOMContentLoaded', function () {
    const toggleGraphBtn = document.getElementById('toggleGraphBtn');
    const graphContainer = document.getElementById('graphContainer');

    toggleGraphBtn.addEventListener('click', function () {
        if (graphContainer.style.display === 'none' || graphContainer.style.display === '') {
            graphContainer.style.display = 'block';
        } else {
            graphContainer.style.display = 'none';
        }
    });
});