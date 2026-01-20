import { describe, it, expect } from "vitest";
import { render, screen } from "@/tests/utils/test-utils";
import { Badge } from "@/components/ui/badge";

describe("Badge", () => {
  it("renders badge with text", () => {
    render(<Badge>Active</Badge>);
    expect(screen.getByText("Active")).toBeInTheDocument();
  });

  it("applies default variant styles", () => {
    const { container } = render(<Badge>Default</Badge>);
    const badge = container.querySelector("div");
    expect(badge).toHaveClass("bg-primary");
  });

  it("applies success variant styles", () => {
    const { container } = render(<Badge variant="success">Success</Badge>);
    const badge = container.querySelector("div");
    expect(badge).toHaveClass("bg-green-100");
  });

  it("applies error variant styles", () => {
    const { container } = render(<Badge variant="error">Error</Badge>);
    const badge = container.querySelector("div");
    expect(badge).toHaveClass("bg-red-100");
  });

  it("applies warning variant styles", () => {
    const { container } = render(<Badge variant="warning">Warning</Badge>);
    const badge = container.querySelector("div");
    expect(badge).toHaveClass("bg-yellow-100");
  });

  it("applies info variant styles", () => {
    const { container } = render(<Badge variant="info">Info</Badge>);
    const badge = container.querySelector("div");
    expect(badge).toHaveClass("bg-blue-100");
  });
});
