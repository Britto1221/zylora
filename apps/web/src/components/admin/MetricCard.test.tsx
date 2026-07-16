import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MetricCard } from "./MetricCard";

describe("MetricCard", () => {
  it("renders a label and value", () => {
    render(<MetricCard label="Clients" value="12" />);
    expect(screen.getByText("Clients")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
  });
});
