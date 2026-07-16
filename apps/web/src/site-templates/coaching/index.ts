import type { PublishedWebsite } from "../shared/types";

export const coachingTemplate: PublishedWebsite = {
  tenantSlug: "example-coaching",
  templateKey: "coaching",
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
        heading: "Coaching landing page",
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
