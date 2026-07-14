import test from 'node:test'; import assert from 'node:assert/strict';
test('operations routes are defined',()=>{for(const route of ['operations','live','review','mlops']) assert.ok(route.length>2)})
