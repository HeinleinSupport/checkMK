/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import userEvent from '@testing-library/user-event'
import { render, screen } from '@testing-library/vue'
import { describe, expect, it, test } from 'vitest'

import ScheduleDowntimeForm, {
  type ScheduleDowntimeFormValues,
  defaultScheduleDowntimeValues,
  downtimeWindow,
  isScheduleDowntimeValid
} from '@/monitoring/shared/components/action/actions/ScheduleDowntimeForm.vue'

function mountForm(overrides: Partial<ScheduleDowntimeFormValues> = {}) {
  const modelValue: ScheduleDowntimeFormValues = {
    ...defaultScheduleDowntimeValues(),
    ...overrides
  }
  return render(ScheduleDowntimeForm, { props: { modelValue } })
}

test('is invalid until a comment is provided', async () => {
  const { emitted } = mountForm()

  expect(emitted('update:valid')?.at(-1)).toEqual([false])

  await userEvent.type(screen.getByPlaceholderText('What is the occasion?'), 'maintenance')
  expect(emitted('update:valid')?.at(-1)).toEqual([true])
})

test('reveals the advanced options when the section is expanded', async () => {
  mountForm({ comment: 'maintenance' })

  const childHosts = screen.getByText('Only for hosts: Set child hosts in downtime.')
  expect(childHosts).not.toBeVisible()

  await userEvent.click(screen.getByRole('button', { name: /Advanced option/ }))
  expect(childHosts).toBeVisible()
})

describe('isScheduleDowntimeValid', () => {
  it('requires a non-empty comment', () => {
    expect(isScheduleDowntimeValid({ ...defaultScheduleDowntimeValues(), comment: '' })).toBe(false)
    expect(isScheduleDowntimeValid({ ...defaultScheduleDowntimeValues(), comment: 'x' })).toBe(true)
  })

  it('rejects a zero ad hoc duration', () => {
    expect(
      isScheduleDowntimeValid({
        ...defaultScheduleDowntimeValues(),
        comment: 'x',
        selection: 'adhoc',
        adhocHours: 0,
        adhocMinutes: 0
      })
    ).toBe(false)
  })
})

describe('downtimeWindow', () => {
  it('spans the preset duration for a preset selection', () => {
    const window = downtimeWindow({ ...defaultScheduleDowntimeValues(), selection: '4h' })

    expect(window).not.toBeNull()
    const spanMs = new Date(window!.end).getTime() - new Date(window!.start).getTime()
    expect(spanMs).toBe(4 * 60 * 60_000)
  })

  it('returns null for an empty ad hoc duration', () => {
    const window = downtimeWindow({
      ...defaultScheduleDowntimeValues(),
      selection: 'adhoc',
      adhocHours: 0,
      adhocMinutes: 0
    })

    expect(window).toBeNull()
  })
})
