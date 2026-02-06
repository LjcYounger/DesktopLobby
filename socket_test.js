const net = require('net');

const client = new net.Socket();
client.connect(10000, '192.168.0.104', () => {
    console.log('Connected');
    const message = JSON.stringify(['text', {'content_list': ['Hello from Node.js!'], 'emotion': 'smile'}]);
    client.write(message);
    client.destroy();
});