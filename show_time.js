window.addEventListener('DOMContentLoaded', () => {
  // When the dom content has been loaded do this
  const messages = document.createElement('ul')
  document.body.appendChild(messages)

  // This is first with the old server
  const websocket = new WebSocket('ws://localhost:5678')
  websocket.onmessage = ({ data }) => {
    const message = document.createElement('li')
    const content = document.createTextNode(data)

    // oooh nice
    message.appendChild(content)
    messages.appendChild(message)
  }
})
