function initTiles(tiles) {
    var tilesContainer = $('#tiles');
    tiles.forEach(function(tile, index) {
        var tileElement = $('<a>')
            .addClass('tile col-md-4') // Change 'col-md-4' to 'col-md-*' to adjust the number of tiles per row
            .attr('href', tile.url)
            .append($('<img>').addClass('tile-image').attr('src', tile.image))
            .append($('<h2>').addClass('tile-title').text(tile.title))
            .append($('<p>').addClass('tile-description').text(tile.description));
        tilesContainer.append(tileElement);

        // Animate tiles sequentially
        setTimeout(function() {
            tileElement.css('opacity', 1); // Set opacity to 1 to make the tile visible
        }, index * 100); // Delay each tile by 200 milliseconds
    });
}
