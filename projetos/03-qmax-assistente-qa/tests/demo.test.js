const test = require('node:test');
const assert = require('node:assert/strict');
const {demoAnswer} = require('../server.js');

test('o modo demo sinaliza simulação sem Azure', () => {
  assert.match(demoAnswer('Como testar uma API REST?'), /DEMONSTRAÇÃO/);
  assert.match(demoAnswer('Como encontrar bugs?'), /Documente/);
});
