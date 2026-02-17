/**
 * Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
 * This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
 * conditions defined in the file COPYING, which is part of this source code package.
 */
import { Folder, Page } from '@demo/_demo/types/page'

import DemoCmkBadge from './basic-elements/DemoCmkBadge.vue'
import DemoCmkButton from './basic-elements/DemoCmkButton.vue'
import DemoCmkChip from './basic-elements/DemoCmkChip.vue'
import DemoCmkCode from './basic-elements/DemoCmkCode.vue'
import DemoCmkColorPicker from './basic-elements/DemoCmkColorPicker.vue'
import DemoCmkSwitch from './basic-elements/DemoCmkSwitch.vue'
import DemoCmkAccordion from './content-organization/CmkAccordion/DemoCmkAccordion.vue'
import DemoCmkSlideInDialog from './content-organization/CmkAccordion/DemoCmkSlideInDialog.vue'
import DemoCmkAccordionStepPanel from './content-organization/CmkAccordionStepPanel/DemoAccordionCmkStepPanel.vue'
import DemoCmkTabs from './content-organization/CmkTabs/DemoCmkTabs.vue'
import DemoCmkWizard from './content-organization/CmkWizard/DemoCmkWizard.vue'
import DemoCmkCatalogPanel from './content-organization/DemoCmkCatalogPanel.vue'
import DemoCmkCollapsible from './content-organization/DemoCmkCollapsible.vue'
import DemoCmkScrollContainer from './content-organization/DemoCmkScrollContainer.vue'
import DemoCmkSlideIn from './content-organization/DemoCmkSlideIn.vue'
import DemoTwoFactorAuth from './content-organization/DemoTwoFactorAuthentication.vue'
import { pages as formElementPages } from './form-elements'
import DemoCmkCheckbox from './form-elements/DemoCmkCheckbox.vue'
import DemoCmkDropdown from './form-elements/DemoCmkDropdown.vue'
import DemoCmkDualList from './form-elements/DemoCmkDualList.vue'
import DemoCmkInput from './form-elements/DemoCmkInput.vue'
import DemoCmkList from './form-elements/DemoCmkList.vue'
import DemoCmkToggleButtonGroup from './form-elements/DemoCmkToggleButtonGroup.vue'
import DemoCmkIcon from './foundation-elements/CmkIcon/DemoCmkIcon.vue'
import DemoCmkIconEmblem from './foundation-elements/CmkIcon/DemoCmkIconEmblem.vue'
import DemoCmkMultitoneIcon from './foundation-elements/CmkIcon/DemoCmkMultitoneIcon.vue'
import DemoCmkHtml from './foundation-elements/DemoCmkHtml.vue'
import DemoCmkIndent from './foundation-elements/DemoCmkIndent.vue'
import DemoCmkKeyboardKey from './foundation-elements/DemoCmkKeyboardKey.vue'
import DemoCmkLabelRequired from './foundation-elements/DemoCmkLabelRequired.vue'
import DemoCmkSpace from './foundation-elements/DemoCmkSpace.vue'
import DemoCmkZebra from './foundation-elements/DemoCmkZebra.vue'
import DemoI18n from './foundation-elements/typography/DemoI18n.vue'
import DemoTypography from './foundation-elements/typography/DemoTypography.vue'
import DemoCmkLinkCard from './navigation/DemoCmkLinkCard.vue'
import DemoCmkAlertBox from './system-feedback/DemoCmkAlertBox.vue'
import DemoCmkDialog from './system-feedback/DemoCmkDialog.vue'
import DemoCmkInlineValidation from './system-feedback/DemoCmkInlineValidation.vue'
import DemoCmkLoading from './system-feedback/DemoCmkLoading.vue'
import DemoCmkPerfometer from './system-feedback/DemoCmkPerfometer.vue'
import DemoCmkPopupDialog from './system-feedback/DemoCmkPopupDialog.vue'
import DemoCmkProgressbar from './system-feedback/DemoCmkProgressbar.vue'
import DemoCmkSkeleton from './system-feedback/DemoCmkSkeleton.vue'
import DemoCmkTooltip from './system-feedback/DemoCmkTooltip.vue'
import DemoErrorBoundary from './system-feedback/DemoErrorBoundary.vue'
import DemoHelp from './system-feedback/DemoHelp.vue'

const basicElementsPages = [
  new Page('CmkBadge', DemoCmkBadge),
  new Page('CmkButton', DemoCmkButton),
  new Page('CmkChip', DemoCmkChip),
  new Page('CmkCode', DemoCmkCode),
  new Page('CmkColorPicker', DemoCmkColorPicker),
  new Page('CmkSwitch', DemoCmkSwitch)
]

const contentOrganizationPages = [
  new Page('CmkAccordion', DemoCmkAccordion),
  new Page('CmkAccordionStepPanel', DemoCmkAccordionStepPanel),
  new Page('CmkTabs', DemoCmkTabs),
  new Page('CmkCatalogPanel', DemoCmkCatalogPanel),
  new Page('CmkCollapsible', DemoCmkCollapsible),
  new Page('CmkScrollContainer', DemoCmkScrollContainer),
  new Page('CmkSlideIn', DemoCmkSlideIn),
  new Page('CmkSlideInDialog', DemoCmkSlideInDialog),
  new Page('CmkWizard', DemoCmkWizard),
  new Page('TwoFactorAuth', DemoTwoFactorAuth)
]

const formElementsPages = [
  new Page('CmkCheckbox', DemoCmkCheckbox),
  new Page('CmkDropdown', DemoCmkDropdown),
  new Page('CmkDualList', DemoCmkDualList),
  new Page('CmkInput', DemoCmkInput),
  new Page('CmkList', DemoCmkList),
  new Page('CmkToggleButtonGroup', DemoCmkToggleButtonGroup),
  ...formElementPages
]

const foundationElementsPages = [
  new Page('CmkIcon', DemoCmkIcon),
  new Page('CmkIconEmblem', DemoCmkIconEmblem),
  new Page('CmkMultitoneIcon', DemoCmkMultitoneIcon),
  new Page('Typography', DemoTypography),
  new Page('i18n', DemoI18n),
  new Page('CmkHtml', DemoCmkHtml),
  new Page('CmkIndent', DemoCmkIndent),
  new Page('CmkKeyboardKey', DemoCmkKeyboardKey),
  new Page('CmkLabelRequired', DemoCmkLabelRequired),
  new Page('CmkSpace', DemoCmkSpace),
  new Page('CmkZebra', DemoCmkZebra)
]

const navigationPages = [new Page('CmkLinkCard', DemoCmkLinkCard)]

const systemFeedbackPages = [
  new Page('CmkAlertBox', DemoCmkAlertBox),
  new Page('CmkDialog', DemoCmkDialog),
  new Page('CmkErrorBoundary', DemoErrorBoundary),
  new Page('CmkHelpText', DemoHelp),
  new Page('CmkInlineValidation', DemoCmkInlineValidation),
  new Page('CmkLoading', DemoCmkLoading),
  new Page('CmkPerfometer', DemoCmkPerfometer),
  new Page('CmkPopupDialog', DemoCmkPopupDialog),
  new Page('CmkProgressbar', DemoCmkProgressbar),
  new Page('CmkSkeleton', DemoCmkSkeleton),
  new Page('CmkTooltip', DemoCmkTooltip)
]

export const roots = [
  new Folder(
    'Components',
    [
      new Folder('Basic elements', basicElementsPages, true),
      new Folder('Content organization', contentOrganizationPages, true),
      new Folder('Form elements', formElementsPages),
      new Folder('Foundation elements', foundationElementsPages),
      new Folder('Navigation', navigationPages),
      new Folder('System feedback', systemFeedbackPages)
    ],
    true
  )
]
