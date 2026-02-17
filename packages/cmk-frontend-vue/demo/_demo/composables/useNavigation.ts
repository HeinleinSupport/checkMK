/**
 * Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { roots } from '@demo/components/'
import { type Component, type Ref, ref } from 'vue'

import { type Folder, Page } from '../types/page'

export interface NavPage {
  type: 'page'
  name: string
  path: string
  component: Component<{ screenshotMode: boolean }>
}

export interface NavFolder {
  type: 'folder'
  name: string
  path: string
  isOpen: Ref<boolean>
  children: Array<NavPage | NavFolder>
}

export type NavItem = NavPage | NavFolder

function buildNavTree(items: Array<Page | Folder>, parentPath: string): Array<NavItem> {
  return items
    .map((item): NavItem => {
      const itemPath = `${parentPath}/${encodeURIComponent(item.name)}`
      if (item instanceof Page) {
        return {
          type: 'page' as const,
          name: item.name,
          path: itemPath,
          component: item.component
        }
      } else {
        return {
          type: 'folder' as const,
          name: item.name,
          path: itemPath,
          isOpen: ref(item.defaultOpen),
          children: buildNavTree(item.pages, itemPath)
        }
      }
    })
    .sort((a, b) => a.name.localeCompare(b.name))
}

const navTrees = buildNavTree(roots, '') as NavFolder[]

export function useNavigation() {
  function openPathToRoute(routePath: string) {
    const segments = routePath.split('/').filter(Boolean)
    let items: NavItem[] = navTrees

    for (const segment of segments) {
      const folder = items.find(
        (item): item is NavFolder =>
          item.type === 'folder' && item.name === decodeURIComponent(segment)
      )
      if (folder) {
        folder.isOpen.value = true
        items = folder.children
      } else {
        break
      }
    }
  }

  return {
    navTrees,
    openPathToRoute
  }
}
