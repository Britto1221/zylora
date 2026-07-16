import type { PublishedWebsite, WebsiteSection } from "./types";

const leadForm: WebsiteSection = {
  id: "contact",
  type: "lead-form",
  visible: true,
  content: {
    eyebrow: "Contact",
    heading: "Start a conversation",
    body: "Send your details and the team will respond directly.",
    fields: ["name", "email", "phone", "service", "message", "whatsappConsent"],
    submitLabel: "Send enquiry",
    successMessage: "Thank you. Your enquiry has been received.",
  },
};

export function exampleWebsite(
  templateKey: string,
  businessName: string,
  heroHeading: string,
  serviceNames: string[],
): PublishedWebsite {
  return {
    siteId: `example-${templateKey}-site`,
    tenantId: `example-${templateKey}-tenant`,
    tenantSlug: `example-${templateKey}`,
    templateKey,
    theme: {
      primaryColor: "#111111",
      secondaryColor: "#2a2a2a",
      accentColor: "#111111",
      backgroundColor: "#ffffff",
      surfaceColor: "#f3f3f3",
      textColor: "#111111",
      mutedColor: "#666666",
      headingFont: "Inter",
      bodyFont: "Inter",
      radius: 14,
      sectionSpacing: 88,
      mode: "light",
    },
    content: {
      businessName,
      navigation: [
        { label: "Services", href: "#services" },
        { label: "About", href: "#about" },
        { label: "Contact", href: "#contact" },
      ],
      sections: [
        {
          id: "hero",
          type: "hero",
          visible: true,
          content: {
            eyebrow: businessName,
            heading: heroHeading,
            body: "A polished example powered by Zylora’s structured publishing system.",
            primaryButton: "Contact us",
            primaryHref: "#contact",
            secondaryButton: "View services",
            secondaryHref: "#services",
          },
        },
        {
          id: "services",
          type: "services",
          visible: true,
          content: {
            eyebrow: "Services",
            heading: "What we offer",
            body: "Clear, outcome-focused services presented for prospective customers.",
            items: serviceNames.map((title) => ({
              title,
              description: `Professional ${title.toLowerCase()} delivered by the team.`,
            })),
          },
        },
        {
          id: "about",
          type: "about",
          visible: true,
          content: {
            eyebrow: "About",
            heading: `Why choose ${businessName}`,
            body: "Trusted service, responsive communication, and a straightforward customer experience.",
            points: ["Experienced team", "Transparent process", "Responsive support"],
          },
        },
        leadForm,
      ],
      footer: {
        summary: `${businessName} — a Zylora example website.`,
        email: "hello@example.com",
        phone: "+1 555 0100",
        address: "Example business address",
      },
    },
    seo: {
      title: `${businessName} | Official Website`,
      description: `${businessName} services, information, and enquiry form.`,
    },
    features: {
      analytics: true,
      chatbot: false,
    },
  };
}
