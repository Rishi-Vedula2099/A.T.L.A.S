"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, signup } from "@/lib/api";
import { setTokens } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      const tokens = await signup(email, password);
      setTokens(tokens.access_token, tokens.refresh_token);
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.status === 409 ? "Email already registered." : err.message);
      } else {
        setError("Signup failed. Is the backend reachable?");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#020408] p-4">
      <Card className="glass-panel w-full max-w-md border-cyber-cyan/30 bg-[rgba(10,14,23,0.7)]">
        <CardHeader>
          <CardTitle className="font-orbitron text-center text-lg tracking-widest text-cyber-cyan">
            ATLAS // REQUEST ACCESS
          </CardTitle>
          <p className="text-center text-xs text-muted-foreground">
            Register a new operator account
          </p>
        </CardHeader>
        <CardContent>
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
              <Label htmlFor="password">Password (min 8 chars)</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
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
              {loading ? "CREATING..." : "CREATE ACCOUNT"}
            </Button>
            <p className="text-center text-xs text-muted-foreground">
              Already registered?{" "}
              <Link href="/login" className="text-cyber-cyan hover:underline">
                Sign in
              </Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
