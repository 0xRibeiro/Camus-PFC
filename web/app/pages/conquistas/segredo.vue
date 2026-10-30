<!-- cantinho secreto do Camus, dedicado a uma discussão muito específica e não será colocado no projeto completo. provavelmente. -->
<template>
  <section class="segredo">
    <div class="conteudo">
      <header class="cabecalho">
        <div>
          <div class="etiqueta">
            <UIcon name="i-lucide-key-round" />
            <span>EASTER EGG ENCONTRADO</span>
          </div>

          <p class="subtitulo">
            Você chegou ao departamento de debates desnecessariamente intensos.
          </p>

          <h1>
            transparente<br>
            <span>não é cor.</span>
          </h1>

          <p class="introducao">
            Sim, criamos uma página inteira para defender esse ponto.
            E trouxemos um aquário como testemunha.
          </p>
        </div>

        <div class="mascote">
          <div
            class="orbita"
            aria-hidden="true"
          />

          <img
            src="/camus-logo-inicial.png"
            alt="Logo do Camus"
            width="240"
            height="240"
          >

          <span class="legenda-mascote">
            esboço da logo super rara do camus
          </span>
        </div>
      </header>

      <div class="explicacao">
        <article>
          <span class="numero">01</span>

          <h2>
            Cor é sobre a luz que chega aos olhos.
          </h2>

          <p>
            Os materiais podem refletir, absorver e transmitir diferentes
            comprimentos de onda da luz. A combinação que chega aos nossos
            olhos participa da percepção das cores.
          </p>

          <div
            class="espectro"
            aria-hidden="true"
          />
        </article>

        <article>
          <span class="numero">02</span>

          <h2>
            Transparência é sobre conseguir ver através.
          </h2>

          <p>
            Um material transparente deixa a luz atravessar com pouca
            dispersão, permitindo distinguir o que está atrás dele.
            Isso descreve uma propriedade óptica do material.
          </p>

          <div class="palavras">
            <span>luz</span>
            <UIcon
              name="i-lucide-arrow-right"
              aria-hidden="true"
            />
            <span class="vidrinho">vidro</span>
            <UIcon
              name="i-lucide-arrow-right"
              aria-hidden="true"
            />
            <UIcon
              name="i-lucide-eye"
              aria-label="Olho"
            />
          </div>
        </article>
      </div>

      <section class="experimento">
        <div class="titulo-experimento">
          <div>
            <p class="mini-etiqueta">
              EXPERIMENTO DE BOLSO
            </p>

            <h2>
              Troque o vidro. Observe o peixe.
            </h2>
          </div>

          <UIcon
            name="i-lucide-flask-conical"
            class="icone-experimento"
            aria-hidden="true"
          />
        </div>

        <p class="descricao-experimento">
          Escolha um material para colocar na frente do aquário.
        </p>

        <div
          class="opcoes"
          role="group"
          aria-label="Material na frente do aquário"
        >
          <button
            v-for="material in materiais"
            :key="material.id"
            type="button"
            :class="{ ativo: selecionado === material.id }"
            :aria-pressed="selecionado === material.id"
            @click="selecionado = material.id"
          >
            {{ material.nome }}
          </button>
        </div>

        <figure>
          <div
            class="aquario"
            role="img"
            :aria-label="materialAtual.descricao"
          >
            <!-- ilustração do cenário atrás do material -->
            <svg
              viewBox="0 0 600 280"
              fill="none"
              aria-hidden="true"
            >
              <defs>
                <linearGradient
                  id="segredo-agua"
                  x1="300"
                  y1="0"
                  x2="300"
                  y2="280"
                  gradientUnits="userSpaceOnUse"
                >
                  <stop stop-color="#cffafe" />
                  <stop
                    offset="1"
                    stop-color="#0891b2"
                  />
                </linearGradient>
              </defs>

              <rect
                width="600"
                height="280"
                fill="url(#segredo-agua)"
              />

              <!-- reflexos da superfície -->
              <path
                d="M0 30 Q75 10 150 30 T300 30 T450 30 T600 30"
                stroke="white"
                stroke-opacity=".55"
                stroke-width="5"
              />
              <path
                d="M0 60 Q75 40 150 60 T300 60 T450 60 T600 60"
                stroke="white"
                stroke-opacity=".2"
                stroke-width="3"
              />

              <!-- areia e vegetação -->
              <path
                d="M0 246 Q150 220 300 246 T600 242 V280 H0Z"
                fill="#fef3c7"
              />
              <path
                d="M70 255 Q35 210 65 175 Q90 210 70 255Z"
                fill="#166534"
              />
              <path
                d="M80 255 Q105 200 90 150 Q65 195 80 255Z"
                fill="#15803d"
              />
              <path
                d="M500 255 Q465 210 495 160 Q520 210 500 255Z"
                fill="#166534"
              />
              <path
                d="M510 255 Q550 220 535 180 Q505 210 510 255Z"
                fill="#22c55e"
              />

              <!-- peixe principal -->
              <g transform="translate(300 135)">
                <path
                  d="M-58 0 L-95 -32 V32Z"
                  fill="#ea580c"
                />
                <ellipse
                  rx="68"
                  ry="40"
                  fill="#fb923c"
                />
                <path
                  d="M-10 -35 Q-25 0 -10 35"
                  stroke="#fff7ed"
                  stroke-width="15"
                />
                <path
                  d="M24 -30 Q10 0 24 30"
                  stroke="#fff7ed"
                  stroke-width="12"
                />
                <path
                  d="M-25 -34 L-5 -58 L20 -36"
                  fill="#ea580c"
                />
                <circle
                  cx="44"
                  cy="-8"
                  r="7"
                  fill="#0f172a"
                />
                <circle
                  cx="46"
                  cy="-10"
                  r="2"
                  fill="white"
                />
                <path
                  d="M54 12 Q61 17 66 10"
                  stroke="#9a3412"
                  stroke-width="3"
                  stroke-linecap="round"
                />
              </g>

              <!-- bolhas -->
              <circle
                cx="405"
                cy="105"
                r="10"
                stroke="white"
                stroke-opacity=".8"
                stroke-width="3"
              />
              <circle
                cx="425"
                cy="72"
                r="6"
                stroke="white"
                stroke-opacity=".6"
                stroke-width="2"
              />
              <circle
                cx="411"
                cy="43"
                r="4"
                stroke="white"
                stroke-opacity=".6"
                stroke-width="2"
              />
            </svg>

            <div
              class="filtro"
              :class="`filtro-${selecionado}`"
            >
              <UIcon
                v-if="selecionado === 'opaco'"
                name="i-lucide-eye-off"
                class="olho-fechado"
              />
            </div>
          </div>

          <figcaption aria-live="polite">
            <strong>{{ materialAtual.titulo }}</strong>
            <p>
              {{ materialAtual.descricao }}
            </p>
          </figcaption>
        </figure>

        <p class="nota">
          Ilustração simplificada: os efeitos reais dependem do material, da sua espessura e da iluminação.
        </p>
      </section>

      <section class="revelacao">
        <UIcon
          name="i-lucide-sparkles"
          class="icone-revelacao"
          aria-hidden="true"
        />

        <div>
          <p class="mini-etiqueta">
            A GRANDE REVELAÇÃO
          </p>

          <h2>
            Transparente também pode ser colorido.
          </h2>

          <p>
            Um vidro azul pode deixar você enxergar através dele enquanto
            transmite alguns comprimentos de onda mais que outros.
            Por isso, “transparente” e “incolor” têm significados diferentes.
          </p>

          <p class="frase-final">
            O peixe continua laranja. O vidro tem seus próprios critérios.
          </p>
        </div>
      </section>

      <footer>
        <UButton
          to="/"
          icon="i-lucide-arrow-left"
          size="lg"
          color="neutral"
        >
          Voltar antes que alguém reabra o debate
        </UButton>

        <p class="fontes">
          A piada veio de graça. A física tem fontes:
          <a
            href="https://openstax.org/books/microbiology/pages/2-1-the-properties-of-light"
            target="_blank"
            rel="noopener noreferrer"
          >OpenStax</a>
          e
          <a
            href="https://micro.magnet.fsu.edu/optics/lightandcolor/filter.html"
            target="_blank"
            rel="noopener noreferrer"
          >Florida State University</a>.
        </p>
      </footer>
    </div>
  </section>
</template>

<script setup lang="ts">
const materiais = [
  {
    id: 'incolor',
    nome: 'Vidro incolor',
    titulo: 'Transparente e incolor',
    descricao: 'Você consegue ver o peixe através do material, com pouca alteração nas cores do cenário.',
  },
  {
    id: 'azul',
    nome: 'Vidro azul',
    titulo: 'Transparente e colorido',
    descricao: 'Você continua vendo o peixe, mas o vidro altera a luz transmitida e a aparência das cores.',
  },
  {
    id: 'opaco',
    nome: 'Placa opaca',
    titulo: 'Colorido e opaco',
    descricao: 'A placa tem cor, mas impede que você veja o peixe através dela. Ele continua atrás do material.',
  },
]

const selecionado = ref('incolor')
const materialAtual = computed(() => materiais.find(material => material.id === selecionado.value) ?? materiais[0]!)
</script>

<style scoped>
.segredo {
  position: relative;
  overflow: hidden;
  padding: clamp(1.25rem, 4vw, 3.5rem);
  border: 1px solid #353253;
  border-radius: 1.5rem;
  color: #eef2ff;
  background:
    radial-gradient(ellipse at 95% 0%, #392468 0%, transparent 45%),
    radial-gradient(ellipse at 0% 60%, #103d49 0%, transparent 45%),
    #101020;
}

.segredo::before {
  position: absolute;
  inset: 0;
  pointer-events: none;
  content: '';
  opacity: .13;
  background-image: radial-gradient(#d8b4fe 1px, transparent 1px);
  background-size: 24px 24px;
}

.conteudo {
  position: relative;
  max-width: 1100px;
  margin: 0 auto;
}

.cabecalho {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 240px;
  align-items: center;
  gap: 2rem;
  padding: 1rem 0 3rem;
}

.etiqueta {
  display: inline-flex;
  align-items: center;
  gap: .6rem;
  padding: .55rem .85rem;
  border: 1px solid #7dd3fc55;
  border-radius: 999px;
  color: #a5f3fc;
  background: #164e6344;
  font-size: .7rem;
  font-weight: 800;
  letter-spacing: .12em;
}

.subtitulo {
  margin-top: 1.25rem;
  color: #b9b8d1;
  font-size: .9rem;
}

h1 {
  margin: 1.1rem 0;
  font-size: clamp(2.7rem, 6vw, 5.5rem);
  font-weight: 900;
  line-height: 1.04;
  letter-spacing: -.055em;
}

h1 span {
  color: #a5f3fc;
  background: linear-gradient(90deg, #a5f3fc, #c4b5fd, #f9a8d4);
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.introducao {
  max-width: 34rem;
  color: #c7c8dd;
  line-height: 1.8;
}

.mascote {
  position: relative;
  display: grid;
  justify-items: center;
  gap: 1rem;
  animation: flutuar 6s ease-in-out infinite;
}

.mascote img {
  position: relative;
  width: 210px;
  height: 210px;
  border: 6px solid #ffffff22;
  border-radius: 50%;
  box-shadow: 0 0 65px #a78bfa33;
}

.orbita {
  position: absolute;
  top: -16px;
  width: 242px;
  height: 242px;
  border: 1px dashed #c4b5fd66;
  border-radius: 50%;
}

.legenda-mascote {
  color: #c4b5fd;
  font-family: monospace;
  font-size: .8rem;
}

.explicacao {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.explicacao article {
  padding: 1.5rem;
  border: 1px solid #ffffff18;
  border-radius: 1.2rem;
  background: #ffffff05;
}

.numero {
  color: #a5f3fc;
  font-family: monospace;
  font-size: .8rem;
}

h2 {
  margin: .7rem 0;
  font-size: clamp(1.2rem, 2.5vw, 1.65rem);
  font-weight: 750;
  line-height: 1.3;
}

.explicacao p, .revelacao p {
  color: #c7c8dd;
  line-height: 1.8;
}

.espectro {
  height: .65rem;
  margin-top: 1.5rem;
  border-radius: 999px;
  background: linear-gradient(90deg, #8b5cf6, #3b82f6, #22d3ee, #4ade80, #fde047, #fb923c, #f87171);
}

.palavras {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .8rem;
  min-height: 2rem;
  margin-top: 1rem;
  color: #a5f3fc;
}

.vidrinho {
  padding: .2rem .8rem;
  border: 1px solid #a5f3fc66;
  border-radius: .4rem;
  background: #a5f3fc0d;
}

.experimento {
  margin-top: 2rem;
  padding: clamp(1rem, 3vw, 2rem);
  border: 1px solid #a5f3fc33;
  border-radius: 1.5rem;
  background: #060c18aa;
}

.titulo-experimento {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.mini-etiqueta {
  color: #a5f3fc !important;
  font-family: monospace;
  font-size: .7rem;
  letter-spacing: .12em;
}

.icone-experimento {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  color: #a5f3fc;
}

.descricao-experimento {
  color: #b9b8d1;
  line-height: 1.7;
}

.opcoes {
  display: flex;
  flex-wrap: wrap;
  gap: .6rem;
  margin: 1.25rem 0;
}

.opcoes button {
  padding: .65rem 1rem;
  border: 1px solid #ffffff26;
  border-radius: .7rem;
  color: #c7c8dd;
  background: #ffffff05;
  cursor: pointer;
  transition: background .2s, border-color .2s;
}

.opcoes button:hover {
  background: #ffffff12;
}

.opcoes button.ativo {
  border-color: #67e8f9;
  color: #cffafe;
  background: #155e7566;
}

.opcoes button:focus-visible {
  outline: 2px solid #f0abfc;
  outline-offset: 4px;
}

.aquario {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  border: 4px solid #cbd5e155;
  border-radius: 1rem;
}

.aquario svg {
  display: block;
  width: 100%;
  height: auto;
}

.filtro {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  pointer-events: none;
  transition: background .35s;
}

.filtro-incolor {
  background: linear-gradient(115deg, transparent 25%, #ffffff22 35%, transparent 45%);
}

.filtro-azul {
  background: #2563eb99;
  mix-blend-mode: multiply;
}

.filtro-opaco {
  background: #6d28d9;
}

.olho-fechado {
  width: 3rem;
  height: 3rem;
  color: #ede9fe;
}

figcaption {
  margin-top: 1.1rem;
}

figcaption strong {
  color: #a5f3fc;
}

figcaption p {
  margin-top: .35rem;
  color: #c7c8dd;
  line-height: 1.7;
}

.nota {
  margin-top: 1rem;
  color: #a3a6bd;
  font-size: .75rem;
  line-height: 1.7;
}

.revelacao {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 2.5rem 0;
}

.icone-revelacao {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  margin-top: .2rem;
  color: #f0abfc;
}

.frase-final {
  margin-top: 1rem;
  color: #f0abfc !important;
  font-style: italic;
}

footer {
  padding-top: 1.5rem;
  border-top: 1px solid #ffffff18;
}

.fontes {
  margin-top: 1.25rem;
  color: #a3a6bd;
  font-size: .75rem;
  line-height: 1.8;
}

.fontes a {
  color: #a5f3fc;
  text-decoration: underline;
  text-underline-offset: 3px;
}

@keyframes flutuar {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@media (max-width: 700px) {
  .cabecalho {
    grid-template-columns: 1fr;
  }

  .mascote {
    grid-row: 1;
    margin: 1rem auto;
  }

  .mascote img {
    width: 150px;
    height: 150px;
  }

  .orbita {
    width: 182px;
    height: 182px;
  }

  .explicacao {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mascote {
    animation: none;
  }

  .filtro, .opcoes button {
    transition: none;
  }
}
</style>
