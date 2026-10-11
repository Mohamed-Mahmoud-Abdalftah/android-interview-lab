import test from 'node:test';
import assert from 'node:assert/strict';
import { addLocalDays, isDue, scheduleReview, validateState } from '../public/scripts/lab-state.mjs';

test('review intervals grow by grade and respect local calendar rollover', () => {
  const day = '2026-10-31';
  assert.equal(scheduleReview({}, 'again', day).due, day);
  assert.equal(scheduleReview({}, 'hard', day).due, '2026-11-01');
  assert.equal(scheduleReview({}, 'good', day).due, '2026-11-02');
  assert.equal(scheduleReview({}, 'easy', day).due, '2026-11-04');
  assert.equal(addLocalDays('2026-12-31', 1), '2027-01-01');
  assert.equal(scheduleReview({ interval: 4 }, 'good', day).interval, 9);
});

test('overdue detection and malformed progress fallback', () => {
  assert.equal(isDue({ due: '2026-10-10' }, '2026-10-11'), true);
  assert.equal(isDue({ due: '2026-10-12' }, '2026-10-11'), false);
  assert.throws(() => validateState({ version: 4, questions: {} }));
  const value = validateState({ version: 1, questions: { 'KOT-01': { status: 'mastered', note: '<script>x</script>' }, 'BAD': {} } }, new Set(['KOT-01']));
  assert.equal(value.questions['KOT-01'].note, '<script>x</script>');
  assert.equal(value.questions.BAD, undefined);
});
