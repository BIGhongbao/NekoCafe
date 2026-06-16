import { test, expect } from '@playwright/test';

test('预约服务 API 旅程：创建→查询→取消', async ({ request }) => {
  const created = await request.post('http://localhost:8081/reservations', {
    data: {
      member_id: 'm001',
      store_id: 'store-bj-001',
      table_id: 't08',
      reserved_at: '2026-06-05T18:30:00+08:00',
      party_size: 2
    }
  });
  expect(created.status()).toBe(201);
  const body = await created.json();

  const detail = await request.get(`http://localhost:8081/reservations/${body.id}`);
  expect(detail.status()).toBe(200);

  const cancelled = await request.delete(`http://localhost:8081/reservations/${body.id}`);
  expect(cancelled.status()).toBe(200);
});
