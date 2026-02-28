import { LoginForm } from "@/components/login-form";

export default function LoginPage() {
  return (
    <div className="fixed inset-0">
      <div className="min-h-screen flex items-center justify-center overflow-auto scrollbar-hide">
        <LoginForm />
        {/*Checking if merger repair was successful */}
      </div>
    </div>
  );
}
