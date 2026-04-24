import { Application, Container, Graphics, Text, TextStyle } from "pixi.js";

export interface AvatarConfig {
  key: string;
  label: string;
  color: number;
  x: number;
  y: number;
}

export class AvatarSprite {
  container: Container;
  private orb: Graphics;
  private pulse: Graphics;
  private label: Text;
  private idleOffset: number;
  baseY: number;
  isActive = false;

  constructor(
    private app: Application,
    private config: AvatarConfig,
  ) {
    this.baseY = config.y;
    this.idleOffset = Math.random() * Math.PI * 2;
    this.container = new Container();
    this.container.x = config.x;
    this.container.y = config.y;

    this.pulse = new Graphics();
    this.pulse.circle(0, 0, 40);
    this.pulse.stroke({ color: config.color, alpha: 0.15, width: 1.5 });
    this.container.addChild(this.pulse);

    this.orb = new Graphics();
    this.orb.circle(0, 0, 28);
    this.orb.fill({ color: config.color, alpha: 0.12 });
    this.orb.circle(0, 0, 28);
    this.orb.stroke({ color: config.color, alpha: 0.7, width: 1.5 });
    this.container.addChild(this.orb);

    const style = new TextStyle({
      fill: 0xe2e8f0,
      fontSize: 10,
      fontFamily: "Inter, DM Sans, sans-serif",
      letterSpacing: 2,
      fontWeight: "600",
    });
    this.label = new Text({
      text: config.label.substring(0, 3).toUpperCase(),
      style,
    });
    this.label.anchor.set(0.5, 0.5);
    this.label.y = 0;
    this.container.addChild(this.label);

    this.container.interactive = true;
    this.container.cursor = "pointer";
    app.ticker.add(this.tick, this);
  }

  private tick = () => {
    const t = this.app.ticker.lastTime / 1000 + this.idleOffset;
    this.container.y = this.baseY + Math.sin(t * 0.6) * 5;
    const pulseScale = 1 + Math.sin(t * 0.8) * 0.08;
    this.pulse.scale.set(pulseScale);
    this.pulse.alpha = this.isActive ? 0.5 : 0.15;
    this.orb.alpha = this.isActive ? 1 : 0.8;
  };

  setActive(active: boolean) {
    this.isActive = active;
  }

  onPointerDown(cb: () => void) {
    this.container.on("pointerdown", cb);
  }

  destroy() {
    this.app.ticker.remove(this.tick, this);
    this.container.destroy({ children: true });
  }
}
