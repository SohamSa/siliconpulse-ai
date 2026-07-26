import { PRODUCT_NAME } from "@/lib/brand";

/**
 * Phase 1 placeholder landing page.
 * Full operational UI begins in Phase 6.
 */
export default function HomePage() {
  return (
    <main className="relative flex min-h-screen flex-col justify-end overflow-hidden px-8 pb-16 pt-24 md:px-16">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_20%_0%,#1a3358_0%,transparent_55%),radial-gradient(ellipse_at_80%_20%,#0f2a24_0%,transparent_45%),linear-gradient(180deg,#0b1220_0%,#070b14_100%)]"
      />
      <div className="relative z-10 max-w-3xl">
        <p className="text-sm tracking-[0.2em] text-slate-400 uppercase">
          Local-first hardware intelligence
        </p>
        <h1 className="mt-4 text-5xl font-semibold tracking-tight text-white md:text-7xl">
          {PRODUCT_NAME}
        </h1>
        <p className="mt-6 max-w-xl text-lg text-slate-300">
          Phase 1 foundation is in place. Runtime fleet observability, digital
          twins, and human-supervised agents arrive in later phases.
        </p>
        <p className="mt-8 text-sm text-slate-500">
          See README.md and docs/product/ROADMAP.md for the build plan.
        </p>
      </div>
    </main>
  );
}
