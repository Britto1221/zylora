export type WebsiteSection = {
  id: string;
  type:
    | "hero"
    | "services"
    | "benefits"
    | "testimonials"
    | "faq"
    | "lead-form"
    | "contact";
  visible: boolean;
  content: Record<string, unknown>;
};

export type WebsiteTheme = {
  primaryColor: string;
  accentColor: string;
  backgroundColor: string;
  headingFont: string;
  bodyFont: string;
  radius: number;
};

export type PublishedWebsite = {
  tenantSlug: string;
  templateKey: "school" | "clinic" | "coaching";
  theme: WebsiteTheme;
  sections: WebsiteSection[];
};
