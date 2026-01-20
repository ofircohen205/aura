import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@/tests/utils/test-utils";
import userEvent from "@testing-library/user-event";
import { LoginForm } from "@/components/auth/LoginForm";
import { useAuthStore } from "@/lib/hooks/useAuth";

// Mock next/navigation
const mockPush = vi.fn();
const mockSearchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => mockSearchParams,
}));

describe("LoginForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPush.mockClear();
    // Reset store state
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      login: async () => {},
      register: async () => {},
      logout: async () => {},
      fetchUser: async () => {},
      setUser: () => {},
    });
  });

  it("renders login form", () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /login/i })).toBeInTheDocument();
  });

  it("shows validation error for invalid email", async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /login/i });

    // Fill in invalid email and valid password
    await user.clear(emailInput);
    await user.type(emailInput, "notanemail");
    await user.type(passwordInput, "password123");

    // Submit form - react-hook-form will validate and show errors
    // Note: HTML5 email validation might prevent submission, but zod validation should still run
    await user.click(submitButton);

    // Wait for form validation to complete and show error
    // react-hook-form validates on submit attempt
    await waitFor(
      () => {
        // Check for the error message - it should appear after form validation
        const errorMessage = screen.queryByText(/invalid email address/i);
        if (!errorMessage) {
          // If not found, check if aria-invalid is set (indicates validation ran)
          const input = screen.getByLabelText(/email/i) as HTMLInputElement;
          if (input.getAttribute("aria-invalid") === "true") {
            // Validation ran, just need to wait for error message to render
            throw new Error("Validation error attribute set but message not visible");
          }
        }
        expect(errorMessage).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it("shows validation error for empty password", async () => {
    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole("button", { name: /login/i });

    await user.type(emailInput, "test@example.com");
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it("calls login function with correct credentials", async () => {
    const mockLogin = vi.fn().mockResolvedValue(undefined);
    const store = useAuthStore.getState();
    useAuthStore.setState({
      ...store,
      login: mockLogin,
    });

    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /login/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      });
    });
  });

  it("displays error message on login failure", async () => {
    const mockLogin = vi.fn().mockRejectedValue(new Error("Invalid credentials"));
    const store = useAuthStore.getState();
    useAuthStore.setState({
      ...store,
      login: mockLogin,
    });

    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /login/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "wrongpassword");

    // Click submit - error is handled by the form component
    await user.click(submitButton);

    // Wait for error to be displayed (the form handles the error internally)
    await waitFor(
      () => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      },
      { timeout: 3000 }
    );

    // Verify login was called
    expect(mockLogin).toHaveBeenCalled();
  });

  it("shows loading state during login", async () => {
    const mockLogin = vi.fn(
      () =>
        new Promise(resolve => {
          setTimeout(resolve, 100);
        })
    );
    const store = useAuthStore.getState();
    useAuthStore.setState({
      ...store,
      login: mockLogin,
    });

    const user = userEvent.setup();
    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole("button", { name: /login/i });

    await user.type(emailInput, "test@example.com");
    await user.type(passwordInput, "password123");
    await user.click(submitButton);

    expect(screen.getByRole("button", { name: /logging in/i })).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });
});
