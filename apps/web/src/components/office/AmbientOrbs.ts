import { Application, Graphics, BlurFilter } from "pixi.js";

export class AmbientOrbs {
  private orbs: Graphics[] = [];

  constructor(private app: Application) {
    this.draw();
  }

  private draw() {
    const { width, height } = this.app.screen;

    const orbDefs = [
      { xPct: 0.12, yPct: 0.18, rPct: 0.32, color: 0x4c1d95, alpha: 0.55 },
      { xPct: 0.88, yPct: 0.78, rPct: 0.24, color: 0x1e3a8a, alpha: 0.4 },
      { xPct: 0.62, yPct: 0.42, rPct: 0.14, color: 0x78350f, alpha: 0.22 },
    ];

    orbDefs.forEach((def) => {
      const g = new Graphics();
      const r = Math.min(width, height) * def.rPct;
      g.circle(width * def.xPct, height * def.yPct, r);
      g.fill({ color: def.color, alpha: def.alpha });

      const blur = new BlurFilter({ strength: 80, quality: 4 });
      g.filters = [blur];

      this.orbs.push(g);
      this.app.stage.addChild(g);
    });
  }

  resize() {
    this.orbs.forEach((g) => g.destroy());
    this.orbs = [];
    this.draw();
  }

  destroy() {
    this.orbs.forEach((g) => g.destroy());
    this.orbs = [];
  }
}
