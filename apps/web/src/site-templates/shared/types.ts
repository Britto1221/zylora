export type WebsiteSection = {
  id: string;
  type: "hero" | "services" | "about" | "testimonials" | "faq" | "lead-form" | "contact" | string;
  visible: boolean;
  variant?: string;
  content: Record<string, unknown>;
};

export type WebsiteTheme = {
  primaryColor: string;
  secondaryColor?: string;
  accentColor?: string;
  backgroundColor: string;
  surfaceColor?: string;
  textColor: string;
  mutedColor?: string;
  headingFont: string;
  bodyFont: string;
  radius: number;
  sectionSpacing?: number;
  mode?: string;
};

export type PublishedWebsite = {
  siteId: string;
  tenantId: string;
  tenantSlug: string;
  templateKey: string;
  content: {
    businessName?: string;
    navigation?: Array<{ label: string; href: string }>;
    sections?: WebsiteSection[];
    footer?: Record<string, unknown>;
  };
  theme: WebsiteTheme;
  seo?: Record<string, unknown>;
  features?: Record<string, boolean>;
  preview?: boolean;
};
