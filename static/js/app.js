document.addEventListener('DOMContentLoaded', () => {

  // --- Theme Toggle Logic Removed (Pure Dark Mode) ---

  // --- Hero Animation (Network Particles) ---
  const canvas = document.getElementById('hero-canvas');
  if (canvas) {
    const ctx = canvas.getContext('2d');
    let width, height;

    const resize = () => {
      width = canvas.width = canvas.parentElement.offsetWidth;
      height = canvas.height = canvas.parentElement.offsetHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const particles = [];
    const particleCount = 40;

    class Particle {
      constructor() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.size = Math.random() * 2 + 1;
      }
      update() {
        this.x += this.vx;
        this.y += this.vy;
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
      }
      draw() {
        ctx.fillStyle = 'rgba(0, 243, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    for (let i = 0; i < particleCount; i++) particles.push(new Particle());

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw connections
      ctx.strokeStyle = 'rgba(0, 243, 255, 0.05)';
      ctx.lineWidth = 1;
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 150) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      particles.forEach(p => {
        p.update();
        p.draw();
      });
      requestAnimationFrame(animate);
    };
    animate();
  }

  // --- Hero Typewriter Effect ---
  // --- Hero Animation (Smooth Fade Up) ---
  const runHeroSequence = () => {
    const h1 = document.getElementById('hero-headline');
    const p = document.getElementById('hero-subtext');

    // Set content directly
    h1.innerHTML = `Efficient RAG <br><span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Without Heavy Infrastructure</span>`;
    p.textContent = "Optimized embedding and generation models running fully locally no API keys, no cloud dependency, and faithful retrieval. Not every task needs a multi-billion parameter cloud model or an API key.";

    // Ensure visibility (in case CSS hid it)
    p.style.opacity = '1';

    // Split text logic for smoother animation would be ideal, 
    // but for "minimal professional", a clean section fade is best.
    // Let's use GSAP if available, otherwise CSS transitions.

    if (typeof gsap !== 'undefined') {
      gsap.fromTo(h1,
        { y: 30, opacity: 0 },
        { y: 0, opacity: 1, duration: 1.2, ease: "power3.out" }
      );

      gsap.fromTo(p,
        { y: 20, opacity: 0 },
        { y: 0, opacity: 1, duration: 1.2, delay: 0.4, ease: "power3.out" }
      );
    } else {
      // Fallback
      h1.style.opacity = 1;
      p.style.opacity = 1;
    }
  };

  // Run sequence
  runHeroSequence();

  // --- Scroll Indicator Logic ---
  const scrollIndicator = document.getElementById('scroll-indicator');
  if (scrollIndicator) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        scrollIndicator.classList.add('opacity-0');
      } else {
        scrollIndicator.classList.remove('opacity-0');
      }
    });
  }

  // --- GSAP Scroll Animations ---
  gsap.registerPlugin(ScrollTrigger);

  // Reveal sections
  gsap.utils.toArray('section').forEach(section => {
    gsap.from(section.children, {
      scrollTrigger: {
        trigger: section,
        start: 'top 80%',
      },
      y: 30,
      opacity: 0,
      duration: 0.8,
      stagger: 0.1,
      ease: 'power2.out'
    });
  });

  // --- Chat Logic ---
  const chatBox = document.getElementById('chat-box');
  const userInput = document.getElementById('user-input');
  const sendBtn = document.getElementById('send-btn');
  const clearBtn = document.getElementById('clear-btn');
  const fileInput = document.getElementById('pdf-upload');
  const uploadArea = document.getElementById('upload-area');

  let isProcessing = false;

  // Helper: Add Message
  const addMessage = (text, type) => {
    const div = document.createElement('div');
    div.className = 'flex gap-4 animate-fade-in-up';

    if (type === 'ai') {
      div.innerHTML = `
                <div class="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary flex-shrink-0 text-xs font-mono">AI</div>
                <div class="text-sm text-text-main leading-relaxed bg-white/5 rounded-2xl rounded-tl-none p-4 max-w-[85%] message-content"></div>
            `;
      // Typewriter effect
      // Typewriter effect
      const contentDiv = div.querySelector('.message-content');

      // Create explicit cursor element
      const cursorSpan = document.createElement('span');
      cursorSpan.className = 'cursor-blink';
      cursorSpan.textContent = '▋';
      contentDiv.appendChild(cursorSpan);

      let i = 0;
      const typeWriter = () => {
        if (i < text.length) {
          // Insert char before cursor
          contentDiv.insertBefore(document.createTextNode(text.charAt(i)), cursorSpan);
          i++;
          chatBox.scrollTop = chatBox.scrollHeight;
          setTimeout(typeWriter, 10); // Speed
        } else {
          cursorSpan.remove();
        }
      };
      chatBox.appendChild(div);
      // Start typing only after append
      if (text) typeWriter();
      else return contentDiv; // Return element for streaming
    } else {
      div.innerHTML = `
                <div class="ml-auto text-sm text-black leading-relaxed bg-white rounded-2xl rounded-tr-none p-4 max-w-[85%]">
                    ${text}
                </div>
            `;
      chatBox.appendChild(div);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
  };

  // Upload
  // Upload Logic
  const uploadInitial = document.getElementById('upload-initial');
  const uploadProgress = document.getElementById('upload-progress');
  const uploadSuccess = document.getElementById('upload-success');

  const progressBar = document.getElementById('progress-bar');
  const progressText = document.getElementById('progress-step-text');
  const progressPercent = document.getElementById('progress-percent');
  const ingestionLogs = document.getElementById('ingestion-logs');
  const resetUploadBtn = document.getElementById('reset-upload-btn');

  // Trigger file click
  uploadInitial.addEventListener('click', () => fileInput.click());

  // Reset Logic
  resetUploadBtn.addEventListener('click', () => {
    uploadSuccess.classList.add('hidden');
    uploadInitial.classList.remove('hidden');
    fileInput.value = ''; // Reset input
  });

  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 1. Transition to Progress State
    uploadInitial.classList.add('hidden');
    uploadProgress.classList.remove('hidden');

    // Reset Progress
    progressBar.style.width = '0%';
    progressPercent.textContent = '0%';
    ingestionLogs.innerHTML = '';

    // Simulated Steps for UX (Simulating the background tasks)
    const steps = [
      { pct: 10, text: `Reading ${file.name}...` },
      { pct: 30, text: 'Parsing PDF Layout...' },
      { pct: 50, text: 'Chunking Text (Sliding Window)...' },
      { pct: 70, text: 'Generating Embeddings (BGE-ONNX)...' },
      { pct: 85, text: 'Building Private FAISS Index...' }
    ];

    let currentStep = 0;

    // Function to add log
    // Function to add log
    const addLog = (msg) => {
      const p = document.createElement('div');
      p.textContent = `> ${msg}`;
      // Use standard Tailwind transition + custom keyframe if available, or simple fade
      p.className = 'opacity-0 transition-opacity duration-500 ease-out text-primary/80';
      ingestionLogs.appendChild(p);

      // Auto-scroll to bottom
      ingestionLogs.scrollTop = ingestionLogs.scrollHeight;

      // Trigger reflow/anim
      requestAnimationFrame(() => {
        p.classList.remove('opacity-0');
      });
    };

    // Simulate progress while waiting for fetch
    const progressInterval = setInterval(() => {
      if (currentStep < steps.length) {
        const step = steps[currentStep];
        progressBar.style.width = `${step.pct}%`;
        progressPercent.textContent = `${step.pct}%`;
        progressText.textContent = step.text;
        addLog(step.text);
        currentStep++;
      }
    }, 1200); // Slower pacing (1.2s) for better readability

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/upload', { method: 'POST', body: formData });

      clearInterval(progressInterval); // Stop simulation

      if (res.ok) {
        // Complete the bar
        progressBar.style.width = '100%';
        progressPercent.textContent = '100%';
        progressText.textContent = 'Ingestion Complete';
        addLog('Done.');

        setTimeout(() => {
          // Transition to Success
          uploadProgress.classList.add('hidden');
          uploadSuccess.classList.remove('hidden');

          userInput.disabled = false;
          userInput.focus();
          addMessage(`Document "${file.name}" ingested successfully. Ready for queries.`, 'ai');
        }, 600);

      } else {
        throw new Error('Upload failed');
      }
    } catch (err) {
      clearInterval(progressInterval);
      uploadProgress.innerHTML = `<p class="text-red-500 text-sm text-center">Error: ${err.message}. Please try again.</p>`;
      console.error(err);
      setTimeout(() => {
        uploadProgress.classList.add('hidden');
        uploadInitial.classList.remove('hidden');
      }, 3000);
    }
  });

  // Ask
  const ask = async () => {
    const text = userInput.value.trim();
    if (!text || isProcessing) return;

    isProcessing = true;
    addMessage(text, 'user');
    userInput.value = '';

    // Prepare AI streaming bubble with THINKING animation
    const div = document.createElement('div');
    div.className = 'flex gap-4 animate-fade-in-up';
    div.innerHTML = `
            <div class="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary flex-shrink-0 text-xs font-mono">AI</div>
            <div class="text-sm text-text-main leading-relaxed bg-white/5 rounded-2xl rounded-tl-none p-4 max-w-[85%] message-content">
                <!-- Thinking Indicator -->
                <div class="flex gap-1 items-center h-5 thinking-dots">
                    <span class="w-1.5 h-1.5 bg-text-muted rounded-full animate-bounce"></span>
                    <span class="w-1.5 h-1.5 bg-text-muted rounded-full animate-bounce" style="animation-delay: 0.1s"></span>
                    <span class="w-1.5 h-1.5 bg-text-muted rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                </div>
            </div>
        `;
    chatBox.appendChild(div);
    const contentDiv = div.querySelector('.message-content');
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
      const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let firstChunk = true;
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // On first chunk, remove thinking dots
        if (firstChunk) {
          contentDiv.innerHTML = '';
          contentDiv.classList.add('typing-cursor');
          firstChunk = false;
        }

        const chunk = decoder.decode(value);
        fullResponse += chunk;

        // Render Markdown
        // Use marked.parse if available, otherwise fallback to text
        if (typeof marked !== 'undefined') {
          contentDiv.innerHTML = marked.parse(fullResponse);
        } else {
          contentDiv.textContent += chunk;
        }

        chatBox.scrollTop = chatBox.scrollHeight;
      }
    } catch (err) {
      contentDiv.innerHTML = "<span class='text-red-500'>[Error generating response]</span>";
    } finally {
      contentDiv.classList.remove('typing-cursor');
      isProcessing = false;
    }
  };

  sendBtn.addEventListener('click', ask);
  userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') ask();
  });

  // Clear
  clearBtn.addEventListener('click', async () => {
    await fetch('/clear', { method: 'POST' });

    // Clear Chat
    chatBox.innerHTML = '';

    // Disable Input
    userInput.disabled = true;

    // Reset Upload UI via visibility toggles (Do NOT overwrite innerHTML)
    const uploadInitial = document.getElementById('upload-initial');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadSuccess = document.getElementById('upload-success');
    const pdfInput = document.getElementById('pdf-upload');
    const logsContainer = document.getElementById('ingestion-logs');
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-step-text');
    const progressPercent = document.getElementById('progress-percent');

    // Reset Values
    if (pdfInput) pdfInput.value = '';
    if (logsContainer) logsContainer.innerHTML = '';
    if (progressBar) progressBar.style.width = '0%';
    if (progressText) progressText.textContent = 'Initializing...';
    if (progressPercent) progressPercent.textContent = '0%';

    // Reset Visibility
    if (uploadInitial) uploadInitial.classList.remove('hidden');
    if (uploadProgress) uploadProgress.classList.add('hidden');
    if (uploadSuccess) uploadSuccess.classList.add('hidden');

    addMessage('Context cleared.', 'ai');
  });

  // --- Model Playground Logic ---
  const pgGenBtn = document.getElementById('pg-gen-btn');
  const pgGenOutput = document.getElementById('pg-gen-output');
  const pgEmbBtn = document.getElementById('pg-emb-btn');
  const pgEmbOutput = document.getElementById('pg-emb-output');

  if (pgGenBtn) {
    pgGenBtn.addEventListener('click', async () => {
      const prompt = document.getElementById('pg-gen-input').value;
      const maxTokens = parseInt(document.getElementById('pg-gen-tokens').value) || 100;
      const temp = parseFloat(document.getElementById('pg-gen-temp').value) || 0.7;

      if (!prompt) return;

      pgGenOutput.textContent = "Generating...";
      pgGenBtn.disabled = true;

      try {
        // Attempting standard HF Inference payload structure
        const response = await fetch('https://abhinavdread-qwen-1-5b-q4-k-m.hf.space/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: prompt,
            max_new_tokens: maxTokens,
            temperature: temp
          })
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        pgGenOutput.textContent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value);
          // Simple append for streaming text
          pgGenOutput.textContent += chunk;
          pgGenOutput.scrollTop = pgGenOutput.scrollHeight;
        }
      } catch (err) {
        pgGenOutput.innerHTML = `<span class="text-red-400">Error: ${err.message}</span><br><br><span class="text-xs text-gray-500">NOTE: If this fails (e.g. Failed to fetch), it is likely a CORS restriction from the Space.</span>`;
        console.error(err);
      } finally {
        pgGenBtn.disabled = false;
      }
    });
  }

  if (pgEmbBtn) {
    pgEmbBtn.addEventListener('click', async () => {
      const text = document.getElementById('pg-emb-input').value;
      if (!text) return;

      pgEmbOutput.textContent = "Computing embeddings...";
      pgEmbBtn.disabled = true;

      try {
        const texts = text.split('\n').filter(t => t.trim());
        // URL FIXED: abhinavdread-bge-en-ft-optimised
        const response = await fetch('https://abhinavdread-bge-en-ft-optimised.hf.space/embed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ chunks: texts })
        });

        if (!response.ok) throw new Error(`API Error: ${response.status}`);

        const data = await response.json();
        pgEmbOutput.textContent = JSON.stringify(data, null, 2);
      } catch (err) {
        pgEmbOutput.innerHTML = `<span class="text-red-400">Error: ${err.message}</span><br><br><span class="text-xs text-gray-500">NOTE: It works best with local proxy, but here we try direct access.</span>`;
        console.error(err);
      } finally {
        pgEmbBtn.disabled = false;
      }
    });
  }

});
