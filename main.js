import { createBoard, playMove } from './connect4.js'

// now we have all the logic needed to transmit moves to the server
function sendMoves(board, websocket) {
  // When clicking a column, send a "play" event for a move in that column.

  // This ensures when this function is called there is no ability to have the event listener called to performn a move
  // Will check out more docs with this
  const params = new URLSearchParams(window.location.search)
  if (params.has('watch')) {
    return
  }

  board.addEventListener('click', ({ target }) => {
    const column = target.dataset.column
    // Ignore clicks outside a column
    if (column == undefined) {
      return
    }
    const event = {
      type: 'play',
      column: parseInt(column, 10),
    }
    websocket.send(JSON.stringify(event))
  })
}

// Going to need 3 types of messages from the server to the browser:
// {type: "play", player: "red", column: 3, row: 0}
// {type: "win", player: "red"}
// {type: "error", "message": "This slot is full."}

function showMessage(message) {
  window.setTimeout(() => window.alert(message), 50)
}

function receiveMoves(board, websocket) {
  websocket.addEventListener('message', ({ data }) => {
    const event = JSON.parse(data)
    switch (event.type) {
      case 'init':
        // Create link for inviting the second player.
        document.querySelector('.join').href = '?join=' + event.join
        // Create a link for watching the game.
        document.querySelector('.watch').href = '?watch=' + event.watch
        break
      case 'play':
        // Update the UI with the move.
        playMove(board, event.player, event.column, event.row)
        break
      case 'win':
        showMessage(`Player ${event.player} wins!`)
        // No further messages are expected; close the WebSocket connection.
        websocket.close(1000)
        break
      case 'error':
        showMessage(event.message)
        break
      default:
        throw new Error(`Unsupported event type: ${event.type}.`)
    }
  })
}

function initGame(websocket) {
  websocket.addEventListener('open', () => {
    // Send an "init" event for the first player.
    const params = new URLSearchParams(window.location.search)
    let event = { type: 'init' }
    if (params.has('join')) {
      // Second player joins an existing game.
      event.join = params.get('join')
    } else if (params.has('watch')) {
      // Watcher joins an existing game.
      event.watch = params.get('watch')
    } else {
      // First player starts a new game.
    }
    websocket.send(JSON.stringify(event))
  })
}

window.addEventListener('DOMContentLoaded', () => {
  // Initialize the UI.
  const board = document.querySelector('.board')
  createBoard(board)
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket('ws://localhost:8001')

  // Initialize the game.
  initGame(websocket)
  receiveMoves(board, websocket)
  sendMoves(board, websocket)
})
