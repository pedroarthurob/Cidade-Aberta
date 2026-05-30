export function Footer() {
  return (
    <footer className="border-t border-border bg-card">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-3">
          <div>
            <h3 className="text-base font-semibold">Cidade Aberta</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Plataforma cidadã de transparência dos gastos públicos da Prefeitura de Campina Grande/PB.
            </p>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Dados</h4>
            <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
              <li>Orçamento municipal</li>
              <li>Licitações e contratos</li>
              <li>Obras públicas</li>
              <li>Indicadores financeiros</li>
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold">Controle social</h4>
            <p className="mt-2 text-sm text-muted-foreground">
              Esta é uma demonstração com dados fictícios para fins de prototipagem. Em produção, os dados serão consumidos
              de APIs oficiais.
            </p>
          </div>
        </div>
        <p className="mt-8 text-xs text-muted-foreground">
          © {new Date().getFullYear()} Cidade Aberta · Iniciativa de transparência pública.
        </p>
      </div>
    </footer>
  );
}
