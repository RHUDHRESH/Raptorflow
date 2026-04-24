import { Application, Graphics } from "pixi.js";
import type { AvatarSprite } from "./AvatarSprite";

export class ConnectionWeb {
  lines: Graphics;
  sprites: AvatarSprite[];
  private time = 0;

  constructor(
    private app: Application,
    sprites: AvatarSprite[],
  ) {
    this.sprites = sprites;
    this.lines = new Graphics();
    app.stage.addChild(this.lines);
    app.ticker.add(this.tick, this);
  }

  private tick = () => {
    this.time += this.app.ticker.deltaTime * 0.008;
    this.redraw();
  };

  private redraw() {
    this.lines.clear();

    const sprites = this.sprites;
    if (sprites.length < 2) return;

    const pairs: [number, number][] = [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
      [5, 0],
      [0, 3],
      [1, 4],
      [2, 5],
    ];

    pairs.forEach(([a, b], idx) => {
      const spriteA = sprites[a];
      const spriteB = sprites[b];

      const x1 = spriteA.container.x;
      const y1 = spriteA.container.y;
      const x2 = spriteB.container.x;
      const y2 = spriteB.container.y;

      const phase = this.time + idx * 0.4;
      const alpha = 0.04 + Math.sin(phase) * 0.03;

      const isActivePair = spriteA.isActive || spriteB.isActive;
      const finalAlpha = isActivePair ? alpha * 4 : alpha;

      this.lines.moveTo(x1, y1);
      this.lines.lineTo(x2, y2);
      this.lines.stroke({ color: 0xffffff, alpha: finalAlpha, width: 1 });
    });
  }

  destroy() {
    this.app.ticker.remove(this.tick, this);
    this.lines.destroy();
  }
}
