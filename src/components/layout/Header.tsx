import { Link } from "@tanstack/react-router";
import { Building2 } from "lucide-react";

export function Header() {
  const nav = [
    { to: "/", label: "Início" },
    { to: "/dashboard", label: "Dashboard" },
    { to: "/licitacoes", label: "Licitações" },
    { to: "/obras", label: "Obras" },
    { to: "/educacao", label: "Educação" },
    { to: "/saude", label: "Saúde" },
    { to: "/empresas", label: "Empresas" },
    { to: "/pergunte", label: "Pergunte aos Dados" },
    { to: "/sobre", label: "Sobre" },
  ] as const;

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Building2 className="h-5 w-5" />
          </span>
          <span className="flex flex-col leading-none">
            <span className="text-base">Cidade Aberta</span>
            <span className="text-[10px] font-normal text-muted-foreground">Campina Grande · PB</span>
          </span>
        </Link>
        <nav className="ml-auto hidden flex-wrap items-center gap-1 lg:flex">
          {nav.map((n) => (
            <Link
              key={n.to}
              to={n.to}
              className="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
              activeProps={{ className: "rounded-md px-3 py-2 text-sm font-medium text-primary bg-primary-soft" }}
            >
              {n.label}
            </Link>
          ))}
        </nav>
        <details className="ml-auto lg:hidden">
          <summary className="cursor-pointer list-none rounded-md border border-border px-3 py-2 text-sm">Menu</summary>
          <div className="absolute right-4 mt-2 w-56 rounded-lg border border-border bg-popover p-2 shadow-lg">
            {nav.map((n) => (
              <Link key={n.to} to={n.to} className="block rounded-md px-3 py-2 text-sm hover:bg-accent">
                {n.label}
              </Link>
            ))}
          </div>
        </details>
      </div>
    </header>
  );
}
