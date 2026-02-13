/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { readonly, ref } from 'vue'

export type Theme = 'facelift' | 'modern-dark'

const currentTheme = ref<Theme>('facelift')

function setTheme(theme: Theme) {
  currentTheme.value = theme
}

function getByTheme<T>(faceliftValue: T, modernDarkValue: T): T {
  return currentTheme.value === 'modern-dark' ? modernDarkValue : faceliftValue
}

export function useTheme() {
  return {
    currentTheme: readonly(currentTheme),
    setTheme,
    getByTheme
  }
}
