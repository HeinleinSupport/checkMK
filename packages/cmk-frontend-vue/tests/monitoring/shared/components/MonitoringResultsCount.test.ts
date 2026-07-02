/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { render, screen } from '@testing-library/vue'
import { ref } from 'vue'

import MonitoringResultsCount from '@/monitoring/shared/components/MonitoringResultsCount.vue'
import { MONITORING_SERVICE } from '@/monitoring/shared/components/MonitoringTableContext'
import type { MonitoringService } from '@/monitoring/shared/services/MonitoringService'

function makeServiceStub(matched = 0, total = 0, committedSearchQuery = '', activeFilterCount = 0) {
  return {
    matched: ref(matched),
    total: ref(total),
    committedSearchQuery: ref(committedSearchQuery),
    filters: { activeFilterCount }
  }
}

function renderCount(stub: ReturnType<typeof makeServiceStub>) {
  return render(MonitoringResultsCount, {
    global: {
      provide: { [MONITORING_SERVICE as symbol]: stub as unknown as MonitoringService<unknown> }
    }
  })
}

test('shows the total row count when nothing narrows the results', () => {
  renderCount(makeServiceStub(42, 42))

  expect(screen.getByText('Total rows: 42')).toBeInTheDocument()
})

// Here we will rely on the banner notice when the limit has been reached.
test('shows the total row count even when matched differs from total', () => {
  renderCount(makeServiceStub(10, 42))

  expect(screen.getByText('Total rows: 42')).toBeInTheDocument()
})

test('shows no count text when there are no matches', () => {
  renderCount(makeServiceStub(0, 0))

  expect(screen.queryByText('Total rows: 0')).not.toBeInTheDocument()
})

test('shows no count text when a search yields no matches', () => {
  renderCount(makeServiceStub(0, 10, 'web'))

  expect(screen.queryByText(/Rows matching your criteria/)).not.toBeInTheDocument()
})

test('keeps the line in the layout so the table does not jump', () => {
  const { container } = renderCount(makeServiceStub(0, 0))

  expect(container.querySelector('.monitoring-results-count')).toBeInTheDocument()
})

test('reacts to the total changing', async () => {
  const stub = makeServiceStub(2, 2)
  renderCount(stub)

  expect(screen.getByText('Total rows: 2')).toBeInTheDocument()

  stub.total.value = 5
  await screen.findByText('Total rows: 5')
})

test('shows the criteria wording when only a search is active', () => {
  renderCount(makeServiceStub(3, 10, 'web'))

  expect(screen.getByText('Rows matching your criteria: 3 | Total rows: 10')).toBeInTheDocument()
})

test('shows the criteria wording when a filter is active', () => {
  renderCount(makeServiceStub(3, 10, '', 1))

  expect(screen.getByText('Rows matching your criteria: 3 | Total rows: 10')).toBeInTheDocument()
})

test('shows the criteria wording when both a filter and a search are active', () => {
  renderCount(makeServiceStub(3, 10, 'web', 2))

  expect(screen.getByText('Rows matching your criteria: 3 | Total rows: 10')).toBeInTheDocument()
})
