/**
 * Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { roots } from '@demo/components/'
import { type RouteLocation, type RouteRecordRaw, createRouter, createWebHistory } from 'vue-router'

import { useNavigation } from '../composables/useNavigation'
import { type Folder, Page } from '../types/page'
import DemoEmpty from '../views/DemoEmpty.vue'
import DemoHome from '../views/DemoHome.vue'

const { openPathToRoute } = useNavigation()

function defaultProps(route: RouteLocation): { screenshotMode: boolean } {
  return { screenshotMode: route.query.screenshot === 'true' }
}

function buildRoutes(items: Array<Page | Folder>, parentPath: string): Array<RouteRecordRaw> {
  const routes: Array<RouteRecordRaw> = []

  for (const item of items) {
    const itemPath = `${parentPath}/${encodeURIComponent(item.name)}`
    if (item instanceof Page) {
      routes.push({
        path: itemPath,
        component: item.component,
        props: defaultProps
      })
    } else {
      routes.push({
        path: itemPath,
        component: DemoEmpty,
        props: defaultProps
      })
      routes.push(...buildRoutes(item.pages, itemPath))
    }
  }
  return routes
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [{ path: '/', component: DemoHome, props: defaultProps }, ...buildRoutes(roots, '')]
})

router.beforeEach((to) => {
  openPathToRoute(to.path)
  return true
})

export default router
