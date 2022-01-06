function random2DIndexOf(array2D, searchElement) {
    let maxRandomNum = 0;
    let random2DIndex = -1;

    for (let i = 0; i < array2D.length; i++) {
        for (let j = 0; j < array2D[i].length; j++) {
            const newRandomNum = Math.random();
            if (array2D[i][j] === searchElement && newRandomNum > maxRandomNum) {
                random2DIndex = [i, j];
                maxRandomNum = newRandomNum;
            }
        }
    }
    return random2DIndex;
};

class Game2048 {
    constructor(rows, columns) {
        this.board = document.getElementById('gameBoard');
        this.grid = document.getElementById('grid');
        this.tileContainer = document.getElementById('tiles');
        this.scoreBoard = document.getElementById("score");

        this.slideEvents = {
            up: this.slideUpEvent.bind(this),
            down: this.slideDownEvent.bind(this),
            left: this.slideLeftEvent.bind(this),
            right: this.slideRightEvent.bind(this),
        };
        this.newGame(rows, columns);
    }

    getEmptyMatrix() {
        return Array.from({length: this.rows}, () => Array(this.columns).fill(null));
    }

    newGame(rows, columns) {
        this.score = 0;
        this.initializeBoard(rows, columns);
        this.addNewTile();
        this.addNewTile();
        this.setAvailableMoves();
    }

    getNewGridElement(gridClass, parent) {
        const newElement = document.createElement('div');
        newElement.classList.add(gridClass);
        parent.appendChild(newElement);
        return newElement;
    };

    createNewGridElement(gridClass, parent) {
        this.getNewGridElement(gridClass, parent);
    };

    initializeGrid() {
        this.grid.replaceChildren();
        for (let i = 0; i < this.rows; i++){
            this.createNewGridElement('gridEdge', this.grid);
            const newRow = this.getNewGridElement('gridRow', this.grid);

            for (let j = 0; j < this.columns; j++) {
                this.createNewGridElement('gridEdge', newRow);
                this.createNewGridElement('gridCell', newRow);
            }
            this.createNewGridElement('gridEdge', newRow);
        }
        this.createNewGridElement('gridEdge', this.grid);
    }

    initializeBoard(rows, columns) {
        this.rows = rows;
        this.columns = columns;
        this.tiles = this.getEmptyMatrix();

        this.initializeGrid();
        this.tileContainer.replaceChildren();

        this.board.focus();
        this.board.classList.remove(...this.board.classList);
        this.board.classList.add(`rows${this.rows}`, `columns${this.columns}`);
    }

    updateScore() {
        this.scoreBoard.innerText = this.score.toLocaleString();
    }

    addNewTile() {
        const [i, j] = random2DIndexOf(this.tiles, null);

        const tile = document.createElement('div');
        tile.rowIdx = i;
        tile.columnIdx = j;
        tile.value = Math.random() < 0.9 ? 2 : 4;
        tile.innerText = tile.value;
        tile.classList.add('tile', `row${i + 1}`, `column${j + 1}`, `value${tile.value}`);

        this.tileContainer.appendChild(tile);
        this.tiles[i][j] = tile;
    }

    hasAdjacentMatchingTile(tile, i, tiles) {
        return tile && tiles[i - 1] && tile.value === tiles[i - 1].value
    }

    isSlideAvailable(direction) {
        const isVerticalShift = ['up', 'down'].includes(direction);
        const maxIdx = isVerticalShift ? this.columns : this.rows;

        for (let i = 0; i < maxIdx; i++) {
            const tiles = isVerticalShift ? this.tiles.map(row => row[i]) : this.tiles[i].map(x => x);
            if (['down', 'right'].includes(direction)) tiles.reverse();

            const idxFirstNull = tiles.indexOf(null);
            const idxFirstTileAfterFirstNull = tiles.findIndex((tile, idx) => (
                tile && idx > idxFirstNull
            ))
            const tilesCanSlide = idxFirstNull >= 0 && idxFirstTileAfterFirstNull >= 0;

            if (tilesCanSlide || tiles.some(this.hasAdjacentMatchingTile)) return true;
        }
        return false;
    }

    setAvailableMoves() {
        for (const direction of ['up', 'down', 'left', 'right']) {
            if (this.isSlideAvailable(direction)) {
                this.board.addEventListener('keyup', this.slideEvents[direction]);
            } else {
                this.board.removeEventListener('keyup', this.slideEvents[direction]);
            }
        }
    }

    computeTileShifts(direction) {
        const isVerticalShift = ['up', 'down'].includes(direction);
        const maxIdx = isVerticalShift ? this.columns : this.rows;

        for (let i = 0; i < maxIdx; i++) {
            let tiles = isVerticalShift ? this.tiles.map(row => row[i]) : this.tiles[i].map(x => x);
            if (['down', 'right'].includes(direction)) tiles.reverse();
            tiles = tiles.filter(Boolean);

            let idxPair = tiles.findIndex(this.hasAdjacentMatchingTile)
            while (idxPair !== -1) {
                tiles[idxPair].mergedWith = tiles[idxPair - 1];
                tiles[idxPair] = null;
                idxPair = tiles.findIndex(this.hasAdjacentMatchingTile)
            }

            tiles.filter(Boolean).forEach((tile, idx) => {
                if (direction === 'up') {
                    tile.newRowIdx = idx;
                    tile.newColumnIdx = i;
                } else if (direction === 'down') {
                    tile.newRowIdx = this.rows - idx - 1;
                    tile.newColumnIdx = i;
                } else if (direction === 'left') {
                    tile.newRowIdx = i;
                    tile.newColumnIdx = idx;
                } else if (direction === 'right') {
                    tile.newRowIdx = i;
                    tile.newColumnIdx = this.columns - idx - 1;
                }
            })
        }
    }

    mergeTiles(tile1, tile2) {
        const oldValue = tile1.value;
        const newValue = 2 * oldValue;
        this.score += newValue;
        tile2.addEventListener('transitionend', () => {
            tile1.innerText = newValue.toLocaleString();
            tile1.classList.replace(`value${oldValue}`, `value${newValue}`);
            tile2.remove();
        })
        const oldRow = tile2.rowIdx + 1;
        const newRow = tile1.newRowIdx + 1;
        tile2.classList.replace(`row${oldRow}`, `row${newRow}`);
        const oldColumn = tile2.columnIdx + 1;
        const newColumn = tile1.newColumnIdx + 1;
        tile2.classList.replace(`column${oldColumn}`, `column${newColumn}`);
        tile1.value = newValue;
    }

    moveTiles() {
        const tilesToUpdate = this.tiles.flat().filter(Boolean);
        this.tiles = this.getEmptyMatrix();

        for(const tile of tilesToUpdate) {
            if (tile.hasOwnProperty('mergedWith')) {
                this.mergeTiles(tile.mergedWith, tile);
            } else {
                const oldRow = tile.rowIdx + 1;
                const newRow = tile.newRowIdx + 1;
                if (oldRow !== newRow) {
                    tile.classList.replace(`row${oldRow}`, `row${newRow}`);
                }
                const oldColumn = tile.columnIdx + 1;
                const newColumn = tile.newColumnIdx + 1;
                if (oldColumn !== newColumn) {
                    tile.classList.replace(`column${oldColumn}`, `column${newColumn}`);
                }

                tile.rowIdx = tile.newRowIdx;
                tile.columnIdx = tile.newColumnIdx;
                this.tiles[tile.rowIdx][tile.columnIdx] = tile;
            }
        }
    }

    slideTiles(direction) {
        this.computeTileShifts(direction);
        this.moveTiles();
        this.updateScore();
        this.addNewTile();
        this.setAvailableMoves();
    }

    slideUpEvent(event) {
        if (event.code === 'ArrowUp' || event.code === 'KeyW') this.slideTiles('up');
    }

    slideDownEvent(event) {
        if (event.code === 'ArrowDown' || event.code === 'KeyS') this.slideTiles('down');
    }

    slideLeftEvent(event) {
        if (event.code === 'ArrowLeft' || event.code === 'KeyA') this.slideTiles('left');
    }

    slideRightEvent(event) {
        if (event.code === 'ArrowRight' || event.code === 'KeyD') this.slideTiles('right');
    }
}

const game2048 = new Game2048(4, 4);
