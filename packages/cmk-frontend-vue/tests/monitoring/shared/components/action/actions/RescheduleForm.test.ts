/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'

import RescheduleForm, {
  type RescheduleValues
} from '@/monitoring/shared/components/action/actions/RescheduleForm.vue'

function mountForm(overrides: Partial<RescheduleValues> = {}) {
  const modelValue: RescheduleValues = { spreadMinutes: 5, ...overrides }
  return render(RescheduleForm, { props: { modelValue } })
}

test('reports valid for a non-negative spread', () => {
  const { emitted } = mountForm()

  expect(emitted('update:valid')?.at(-1)).toEqual([true])
})

test('reports invalid when no spread is entered', () => {
  const { emitted } = mountForm({ spreadMinutes: undefined })

  expect(emitted('update:valid')?.at(-1)).toEqual([false])
})

test('renders the spread-over input', () => {
  mountForm()

  expect(screen.getByText('Spread over')).toBeInTheDocument()
})
