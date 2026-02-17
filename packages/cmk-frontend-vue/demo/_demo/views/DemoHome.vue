<!--
Copyright (C) 2026 Checkmk GmbH - License: GNU General Public License v2
This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
conditions defined in the file COPYING, which is part of this source code package.
-->
<script setup lang="ts">
import demoLayoutImage from '../assets/images/demo-layout.png'
import CtaBanner from '../components/DemoCtaBanner.vue'
import DemoHeroBanner from '../components/DemoHeroBanner.vue'
import HomeLayout from '../components/DemoHomeLayout.vue'
import DemoInfoCard from '../components/DemoInfoCard.vue'

defineProps<{ screenshotMode: boolean }>()
</script>

<template>
  <HomeLayout>
    <template #header>
      <DemoHeroBanner title="Checkmk Vue Demo App" subtitle="UI components behind Checkmk" />
    </template>

    <template #intro>
      <h1>The single source of truth for Checkmk UI components</h1>
      <p>
        Explore, understand, and use Vue UI components consistently across Checkmk — with real
        behavior, real code, and no guesswork.
      </p>

      <div>
        <p><strong>A centralized reference to:</strong></p>
        <ul>
          <li>Discover which UI components exist</li>
          <li>See how components look and behave in reality</li>
          <li>Understand supported variants and states</li>
          <li>Access example usage and source code snippets</li>
          <li>Reduce ambiguity and rework across teams</li>
        </ul>
      </div>
    </template>

    <template #feature-left>
      <h1>What’s included</h1>

      <h2>Components</h2>
      <p>
        Components are reusable, functional UI building blocks built on top of the foundations that
        meet specific interaction needs. They are designed to be consistent, accessible, and
        scalable, and are implemented in Vue for use across different use cases and projects.
      </p>
    </template>

    <template #feature-right>
      <img
        :src="demoLayoutImage"
        alt="Component screenshot"
        style="max-width: 100%; max-height: 100%; object-fit: contain"
      />
    </template>

    <template #audience-title>
      <h1>Audience and usage</h1>
    </template>

    <template #audience-cards>
      <DemoInfoCard
        icon-name="development"
        title="Development"
        variant="borderless"
        :bullet-points="[
          'Use as the first stop before building UI',
          'Search for existing components instead of re-implementing',
          'Review real behavior, variants, and states',
          'Use the detailed page as a reference during implementation and reviews',
          'Base new component usage on the provided structure and examples'
        ]"
      />
      <DemoInfoCard
        icon-name="ux"
        title="UX"
        variant="borderless"
        :bullet-points="[
          'Use to verify design consistency against what is actually implemented',
          'Validate that components behave as expected across states',
          'Use it as a shared reference when discussing design decisions with developers',
          'Identify potential design gaps or inconsistencies before development'
        ]"
      />
      <DemoInfoCard
        icon-name="product"
        title="Product"
        variant="borderless"
        :bullet-points="[
          'Use as a shared reference during feature discussions',
          'Validate what UI components already exist before proposing new ones',
          'Align expectations with Development and UX using a common, concrete baseline',
          'Reduce ambiguity in requirements by referencing existing components and behavior'
        ]"
      />
      <DemoInfoCard
        icon-name="qa"
        title="QA"
        variant="borderless"
        :bullet-points="[
          'Use as a baseline for expected behavior',
          'Validate UI behavior and states against what is documented in the component pages',
          'Identify inconsistencies between implemented features and component definitions',
          'Use it to support regression testing and exploratory testing scenarios'
        ]"
      />
    </template>

    <template #cta>
      <CtaBanner
        title="Design System documentation"
        subtitle="Explore detailed guidelines, usage principles, and processes in our Design System documentation. This space provides additional context to help you design, build, and maintain consistent components."
        button-text="View documentation"
        button-url="https://www.checkmk.com"
      />
    </template>
  </HomeLayout>
</template>
