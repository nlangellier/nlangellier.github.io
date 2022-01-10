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
    constructor() {
        this.board = document.getElementById('gameBoard');
        this.grid = document.getElementById('grid');
        this.tileContainer = document.getElementById('tiles');
        this.scoreBoard = document.getElementById("score");
        this.rowSelector = document.getElementById("rowSelector");
        this.columnSelector = document.getElementById("columnSelector");
        this.gameOverMessage = document.getElementById("gameOverMessage");
        this.newGameButton = document.getElementById("newGameButton");
        this.hintButton = document.getElementById("hintButton");
        this.hintText = document.getElementById("hintText");

        this.isAvailable = {up: false, down: false, left: false, right: false};
        this.touchX0 = 0;
        this.touchX1 = 0;
        this.touchY0 = 0;
        this.touchY1 = 0;

        this.newGameButton.addEventListener("click", this.newGame.bind(this));
        this.hintButton.addEventListener('click', this.getAIHint.bind(this));
        this.board.addEventListener('keyup', this.keyUpEvent.bind(this));
        this.board.addEventListener('touchstart', this.touchStartEvent.bind(this));
        this.board.addEventListener('touchend', this.touchEndEvent.bind(this));

        this.newGame();
    }

    getEmptyMatrix() {
        return Array.from({length: this.rows}, () => Array(this.columns).fill(null));
    }

    newGame() {
        this.score = 0;
        this.hintText.innerText = "";
        this.updateScoreBoard();
        this.gameOverMessage.classList.remove("visibility");
        this.initializeBoard();
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

    initializeBoard() {
        this.rows = parseInt(this.rowSelector.value);
        this.columns = parseInt(this.columnSelector.value);
        this.tiles = this.getEmptyMatrix();

        this.initializeGrid();
        this.tileContainer.replaceChildren();

        this.board.focus();
        this.board.classList.remove(...this.board.classList);
        this.board.classList.add(`rows${this.rows}`, `columns${this.columns}`);
    }

    updateScoreBoard() {
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
        let gameOver = true;
        for (const direction of ['up', 'down', 'left', 'right']) {
            if (this.isSlideAvailable(direction)) {
                this.isAvailable[direction] = true;
                gameOver = false;
            } else {
                this.isAvailable[direction] = false;
            }
        }
        if (gameOver) {
            this.gameOverMessage.classList.add("visibility");
            this.postNewScoreToDatabase();
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
            tile2.addEventListener('animationend', () => {
                tile2.remove();
                tile1.innerText = newValue.toLocaleString();
                const newClass = newValue > 268435456 ? "value268435456" : `value${newValue}`;
                tile1.classList.replace(`value${oldValue}`, newClass);
            })
            tile2.classList.add('mergeAnimation');
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
        if (this.isAvailable[direction]) {
            this.hintText.innerText = "";
            this.isAvailable = {up: false, down: false, left: false, right: false};
            this.computeTileShifts(direction);
            this.moveTiles();
            this.updateScoreBoard();
            this.addNewTile();
            this.setAvailableMoves();
        }
    }

    keyUpEvent(event) {
        if (event.code === 'ArrowUp' || event.code === 'KeyW') {
            this.slideTiles('up');
        } else if (event.code === 'ArrowDown' || event.code === 'KeyS') {
            this.slideTiles('down');
        } else if (event.code === 'ArrowLeft' || event.code === 'KeyA') {
            this.slideTiles('left');
        } else if (event.code === 'ArrowRight' || event.code === 'KeyD') {
            this.slideTiles('right');
        }
    }

    touchStartEvent(event) {
        this.touchX0 = event.changedTouches[0].screenX;
        this.touchY0 = event.changedTouches[0].screenY;
    }

    touchEndEvent(event) {
        this.touchX1 = event.changedTouches[0].screenX;
        this.touchY1 = event.changedTouches[0].screenY;

        const dX = this.touchX1 - this.touchX0;
        const dY = this.touchY0 - this.touchY1;
        if (Math.hypot(dX, dY) < 10) return;

        const theta = Math.atan2(dY, dX);
        if (theta < -3 * Math.PI / 4) {
            this.slideTiles('left');
        } else if (theta < -Math.PI / 4) {
            this.slideTiles('down');
        } else if (theta < Math.PI / 4) {
            this.slideTiles('right');
        } else if (theta < 3 * Math.PI / 4) {
            this.slideTiles('up');
        } else {
            this.slideTiles('left');
        }
    }

    get state() {
        const log2Values = this.tiles.map(row => row.map(tile => (
            tile ? Math.log2(tile.value) : 0
        )));
        return {values: log2Values};
    }

    async getAIHint() {
        const request = new Request("/hint",
                                    {method: "POST",
                                     headers: {"Content-Type": "application/json"},
                                     body: JSON.stringify(this.state)});
        const response = await fetch(request);
        const data = await response.json();
        const hint = data.hint;
        this.hintText.innerText = hint[0].toUpperCase() + hint.slice(1);
        this.board.focus();
    }

    async postNewScoreToDatabase() {
        const gameOverInfo = {
            name: "testing",
            score: this.score,
            rows: this.rows,
            columns: this.columns
        };
        const request = new Request("/add-score",
                                    {method: "POST",
                                     headers: {"Content-Type": "application/json"},
                                     body: JSON.stringify(gameOverInfo)});
        await fetch(request);
    }
}

const game2048 = new Game2048();
