import type { PublishedWebsite } from "../shared/types";

export const clinicTemplate: PublishedWebsite = {
  tenantSlug: "example-clinic",
  templateKey: "clinic",
  theme: {
    primaryColor: "#18181b",
    accentColor: "#2563eb",
    backgroundColor: "#ffffff",
    headingFont: "Inter",
    bodyFont: "Inter",
    radius: 16
  },
  sections: [
    {
      id: "hero",
      type: "hero",
      visible: true,
      content: {
        heading: "Clinic landing page",
        body: "Replace this content from the Zylora admin dashboard."
      }
    },
    {
      id: "lead-form",
      type: "lead-form",
      visible: true,
      content: {
        heading: "Contact us"
      }
    }
  ]
};
