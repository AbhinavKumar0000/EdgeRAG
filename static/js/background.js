document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('hero-canvas');
  const ctx = canvas.getContext('2d');

  let width, height;
  let particles = [];

  // Antigravity Configuration
  const config = {
    particleCount: window.innerWidth < 768 ? 40 : 100,
    connectionDistance: 150,
    mouseDistance: 200,
    speed: 0.5,
    color: '124, 58, 237' // Gravity Violet (RGB)
  };

  // Resize Handler
  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  // Particle Class
  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * config.speed;
      this.vy = (Math.random() - 0.5) * config.speed;
      this.size = Math.random() * 2 + 1;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      // Bounce off edges
      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${config.color}, 0.9)`;
      ctx.fill();
    }
  }

  // Initialize
  function init() {
    resize();
    particles = [];
    for (let i = 0; i < config.particleCount; i++) {
      particles.push(new Particle());
    }
  }

  // Animation Loop
  function animate() {
    ctx.clearRect(0, 0, width, height);

    // Update color based on theme (check CSS var)
    // We read the primary color from computed styles to adapt to theme changes dynamically
    const computedStyle = getComputedStyle(document.documentElement);
    // Simple heuristic: if bg is light, use darker violet, else lighter
    // But for now we stick to config or could parse variable.

    particles.forEach(p => {
      p.update();
      p.draw();
    });

    // Draw Connections
    particles.forEach((a, index) => {
      for (let i = index + 1; i < particles.length; i++) {
        const b = particles[i];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < config.connectionDistance) {
          const opacity = 1 - (distance / config.connectionDistance);
          ctx.beginPath();
          ctx.strokeStyle = `rgba(${config.color}, ${opacity * 0.5})`;
          ctx.lineWidth = 1;
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    });

    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => {
    resize();
    init();
  });

  init();
  animate();
});
