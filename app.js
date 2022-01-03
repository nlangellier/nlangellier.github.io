const arraysEqual2D = function (array1, array2) {
    if (array1.length !== array2.length) return false;

    for (let i = 0; i < array1.length; i++) {
        row1 = array1[i];
        row2 = array2[i];
        if (row1.length !== row2.length) return false;

        for (let j = 0; j < row1.length; j++) {
            if (row1[j] !== row2[j]) return false
        };
    };

    return true;
};

const random2DIndexOf = function (array2D, searchElement) {
    let maxRandomNum = 0;
    let random2DIndex = -1;

    for (let row = 0; row < array2D.length; row++) {
        const rowArray = array2D[row];
        for (let column = 0; column < rowArray.length; column++) {
            const newRandomNum = Math.random();
            if (rowArray[column] === searchElement && newRandomNum > maxRandomNum) {
                random2DIndex = [row, column];
                maxRandomNum = newRandomNum;
            }
        }
    }
    return random2DIndex;
};

const getNewGridElement = function (gridClass, parent) {
    const newElement = document.createElement('div');
    newElement.classList.add(gridClass);
    parent.appendChild(newElement);
    return newElement;
};

const createNewGridElement = function (gridClass, parent) {
    getNewGridElement(gridClass, parent);
};

const slideUpEvent = function (event) {
    if (event.code === 'ArrowUp' || event.code === 'KeyW') {
        game2048.moveTilesUp()
            .then(game2048.updateScore())
            .then(game2048.addNewTile())
            .then(game2048.setAvailableMoves());
    };
};

const slideDownEvent = function (event) {
    if (event.code === 'ArrowDown' || event.code === 'KeyS') {
        game2048.moveTilesDown()
            .then(game2048.updateScore())
            .then(game2048.addNewTile())
            .then(game2048.setAvailableMoves());
    };
};

const slideLeftEvent = function (event) {
    if (event.code === 'ArrowLeft' || event.code === 'KeyA') {
        game2048.moveTilesLeft()
            .then(game2048.updateScore())
            .then(game2048.addNewTile())
            .then(game2048.setAvailableMoves());
    };
};

const slideRightEvent = function (event) {
    if (event.code === 'ArrowRight' || event.code === 'KeyD') {
        game2048.moveTilesRight()
            .then(game2048.updateScore())
            .then(game2048.addNewTile())
            .then(game2048.setAvailableMoves());
    };
};

const game2048 = {
    board: document.getElementById('gameBoard'),
    grid: document.getElementById('grid'),
    tileContainer: document.getElementById('tiles'),

    nextTileMatrix: {},

    getEmptyTileMatrix: function () {
        return Array.from({length: this.rows}, () => Array(this.columns).fill(null));
    },

    newGame: function () {
        this.score = 0;
        this.initializeBoard(4, 4);
        this.addNewTile();
        this.addNewTile()
            .then(this.setAvailableMoves());
    },
    initializeBoard: function (rows, columns) {
        this.grid.replaceChildren();
        this.tileContainer.replaceChildren();

        this.rows = rows;
        this.columns = columns;
        this.tiles = this.getEmptyTileMatrix();

        this.board.focus();
        this.board.classList.remove(...this.board.classList);
        this.board.classList.add(`rows${this.rows}`, `columns${this.columns}`);

        for (let i = 0; i < this.rows; i++){
            createNewGridElement('gridEdge', this.grid);
            const newRow = getNewGridElement('gridRow', this.grid);

            for (let j = 0; j < this.columns; j++) {
                createNewGridElement('gridEdge', newRow);
                createNewGridElement('gridCell', newRow);
            }
            createNewGridElement('gridEdge', newRow);
        }
        createNewGridElement('gridEdge', this.grid);
    },

    updateScore: async function () {
        document.getElementById("score").innerText = this.score.toLocaleString();
    },

    addNewTile: async function () {
        const [row, column] = random2DIndexOf(this.tiles, null);

        const tile = document.createElement('div');
        tile.classList.add('tile', `row${row + 1}`, `column${column + 1}`);

        if (Math.random() < 0.9) {
            tile.innerText = 2;
            tile.classList.add('color2');
        } else {
            tile.innerText = 4;
            tile.classList.add('color4');
        };
        this.tileContainer.appendChild(tile);
        this.tiles[row][column] = tile;
    },

    popTile: function (tile, idx, direction, updateClass, isMerge = false) {
        let oldClass;
        const isVerticalShift = ['up', 'down'].includes(direction);
        const isHorizontalShift = !isVerticalShift;

        for (const className of tile.classList) {
            const isVerticalMatch = isVerticalShift && className.startsWith('row');
            const isHorizontalMatch = isHorizontalShift && className.startsWith('column');
            if (isVerticalMatch || isHorizontalMatch) oldClass = className;
        }

        let newClass;
        let row = idx;
        let column = idx;

        if (direction === 'up') {
            const columnArray = this.nextTileMatrix.up.map(rowArray => rowArray[column]);
            row = columnArray.indexOf(null);
            newClass = isMerge ? `row${row}` : `row${row + 1}`;
        } else if (direction === 'down') {
            const columnArray = this.nextTileMatrix.down.map(rowArray => rowArray[column]);
            row = columnArray.lastIndexOf(null);
            newClass = isMerge ? `row${row + 2}` : `row${row + 1}`;
        } else if (direction === 'left') {
            column = this.nextTileMatrix.left[row].indexOf(null);
            newClass = isMerge ? `column${column}` : `column${column + 1}`;
        } else if (direction === 'right') {
            column = this.nextTileMatrix.right[row].lastIndexOf(null);
            newClass = isMerge ? `column${column + 2}` : `column${column + 1}`;
        }

        if (updateClass) tile.classList.replace(oldClass, newClass);
        if (!isMerge) this.nextTileMatrix[direction][row][column] = tile;
    },
    popBothTiles: function (tile1, tile2, idx, direction, updateClasses) {
        if (updateClasses) {
            tile2.addEventListener('transitionend', () => {
                oldValue = parseInt(tile1.innerText);
                newValue = 2 * oldValue;
                this.score += newValue;
                tile1.innerText = newValue.toLocaleString();
                tile1.classList.replace(`color${oldValue}`, `color${newValue}`);
                tile2.remove();
            });
        };

        this.popTile(tile1, idx, direction, updateClasses, false);
        this.popTile(tile2, idx, direction, updateClasses, true);
    },
    moveTiles: function(direction, updateClasses) {
        const isVerticalShift = ['up', 'down'].includes(direction);
        const arrayLength = isVerticalShift ? this.columns : this.rows;
        const previousTiles = Array(arrayLength).fill(null);

        for (let i = 0; i < this.rows; i++) {
            row = direction === 'up' ? i : this.rows - i -1;
            for (let j = 0; j < this.columns; j++) {
                const column = direction === 'left' ? j : this.columns - j - 1;
                const idx = isVerticalShift ? column : row;
                const currentTile = this.tiles[row][column];

                if (currentTile) {
                    const previousTile = previousTiles[idx];
                    if (previousTile) {
                        if (previousTile.innerText === currentTile.innerText) {
                            this.popBothTiles(previousTile, currentTile, idx, direction, updateClasses);
                            previousTiles[idx] = null;
                        } else {
                            this.popTile(previousTile, idx, direction, updateClasses);
                            previousTiles[idx] = currentTile;
                        }
                    } else {
                        previousTiles[idx] = currentTile;
                    }
                };
            };
        };

        previousTiles.forEach((tile, idx) => {
            if (tile) this.popTile(tile, idx, direction, updateClasses);
        })
    },
    moveTilesUp: async function () {
        this.nextTileMatrix.up = this.getEmptyTileMatrix();
        this.moveTiles('up', true);
        this.tiles = this.nextTileMatrix.up;
    },
    moveTilesDown: async function () {
        this.nextTileMatrix.down = this.getEmptyTileMatrix();
        this.moveTiles('down', true);
        this.tiles = this.nextTileMatrix.down;
    },
    moveTilesLeft: async function () {
        this.nextTileMatrix.left = this.getEmptyTileMatrix();
        this.moveTiles('left', true);
        this.tiles = this.nextTileMatrix.left;
    },
    moveTilesRight: async function () {
        this.nextTileMatrix.right = this.getEmptyTileMatrix();
        this.moveTiles('right', true);
        this.tiles = this.nextTileMatrix.right;
    },

    setAvailableMoves: async function () {
        this.nextTileMatrix.up = this.getEmptyTileMatrix();
        this.moveTiles('up', false);
        if (arraysEqual2D(this.tiles, this.nextTileMatrix.up)) {
            this.board.removeEventListener('keyup', slideUpEvent);
        } else {
            this.board.addEventListener('keyup', slideUpEvent);
        };

        this.nextTileMatrix.down = this.getEmptyTileMatrix();
        this.moveTiles('down', false);
        if (arraysEqual2D(this.tiles, this.nextTileMatrix.down)) {
            this.board.removeEventListener('keyup', slideDownEvent);
        } else {
            this.board.addEventListener('keyup', slideDownEvent);
        };

        this.nextTileMatrix.left = this.getEmptyTileMatrix();
        this.moveTiles('left', false);
        if (arraysEqual2D(this.tiles, this.nextTileMatrix.left)) {
            this.board.removeEventListener('keyup', slideLeftEvent);
        } else {
            this.board.addEventListener('keyup', slideLeftEvent);
        };

        this.nextTileMatrix.right = this.getEmptyTileMatrix();
        this.moveTiles('right', false);
        if (arraysEqual2D(this.tiles, this.nextTileMatrix.right)) {
            this.board.removeEventListener('keyup', slideRightEvent);
        } else {
            this.board.addEventListener('keyup', slideRightEvent);
        };
    }
};

game2048.newGame();
