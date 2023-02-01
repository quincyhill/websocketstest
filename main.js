import { createBoard, playMove } from './connect4.js'

window.addEventListener('DOMContentLoaded', () => {
  // Initialize the UI.
  const board = document.querySelector('.board')
  createBoard(board)
  // Open the WebSocket connection and register event handlers.
  const websocket = new WebSocket('ws://localhost:8001')

  // This is my solution, glad this works but will be doing other stuff
  // websocket.onopen = () => websocket.send('user connected')
  receiveMoves(board, websocket)
  sendMoves(board, websocket)
})

// now we have all the logic needed to transmit moves to the server
function sendMoves(board, websocket) {
  // When clicking a column, send a "play" event for a move in that column.
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