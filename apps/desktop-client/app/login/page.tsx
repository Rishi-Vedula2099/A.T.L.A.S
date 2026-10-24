"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, login } from "@/lib/api";
import { setTokens } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await login(email, password);
      setTokens(tokens.access_token, tokens.refresh_token);
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 401 ? "Invalid credentials." : err.message);
      } else {
        setError("Login failed. Is the backend reachable?");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthShell title="ATLAS // ACCESS PORTAL" subtitle="Authenticate to enter the Control Deck">
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="cyber-input"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="cyber-input"
          />
        </div>
        {error && (
          <p className="text-xs text-destructive" role="alert">
            {error}
          </p>
        )}
        <Button type="submit" disabled={loading} className="cyber-btn w-full">
          {loading ? "AUTHENTICATING..." : "ENTER"}
        </Button>
        <p className="text-center text-xs text-muted-foreground">
          No account?{" "}
          <Link href="/signup" className="text-cyber-cyan hover:underline">
            Request access
          </Link>
        </p>
      </form>
    </AuthShell>
  );
}

export function AuthShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#020408] p-4">
      <Card className="glass-panel w-full max-w-md border-cyber-cyan/30 bg-[rgba(10,14,23,0.7)]">
        <CardHeader>
          <CardTitle className="font-orbitron text-center text-lg tracking-widest text-cyber-cyan">
            {title}
          </CardTitle>
          <p className="text-center text-xs text-muted-foreground">{subtitle}</p>
        </CardHeader>
        <CardContent>{children}</CardContent>
      </Card>
    </div>
  );
}
