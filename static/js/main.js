// ============================================
// Configuração da API
// ============================================
// Se o backend estiver no mesmo domínio, manter vazio.
// Caso contrário, definir a URL base da API.
const apiBase = ''

// ============================================
// Seleção de elementos do DOM
// ============================================
const senhaInput   = document.getElementById('senha')      // Campo de entrada da senha
const avaliarBtn   = document.getElementById('avaliar')    // Botão para avaliar senha
const resultado    = document.getElementById('resultado')  // Área de exibição do resultado
const problemasEl  = document.getElementById('problemas')  // Área de exibição de problemas encontrados
const barra        = document.getElementById('barra')      // Barra de progresso (força da senha)
const toggle       = document.getElementById('toggle')     // Botão para mostrar/ocultar senha
const gerarBtn     = document.getElementById('gerar')      // Botão para gerar senha aleatória
const copiarBtn    = document.getElementById('copiar')     // Botão para copiar senha gerada
const saida        = document.getElementById('saida')      // Campo de saída da senha gerada

// ============================================
// Função para avaliar a senha
// ============================================
async function avaliar() {
  const senha = senhaInput.value

  // Requisição ao backend para avaliação da senha
  const res = await fetch(apiBase + '/avaliar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ senha })
  })

  // Tratamento de erro na requisição
  if (!res.ok) {
    resultado.textContent = 'Erro ao avaliar'
    return
  }

  // Processamento da resposta
  const data = await res.json()

  // Exibição dos resultados
  resultado.textContent = `${data.nivel} — ${data.pontuacao}/100 (${data.entropia_bits} bits)`
  problemasEl.textContent = data.problemas.length
    ? data.problemas.join('\n')
    : 'Boa, essa senha parece segura 👍'

  // Atualização da barra de progresso
  barra.style.width = data.pontuacao + '%'
}

// ============================================
// Alternar visibilidade da senha
// ============================================
toggle.addEventListener('click', () => {
  if (senhaInput.type === 'password') {
    senhaInput.type = 'text'
  } else {
    senhaInput.type = 'password'
  }
})

// ============================================
// Eventos de avaliação
// ============================================
// Avaliar ao clicar no botão
avaliarBtn.addEventListener('click', avaliar)

// Avaliar ao pressionar Enter dentro do campo de senha
senhaInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') avaliar()
})

// ============================================
// Função para gerar senha aleatória
// ============================================
gerarBtn.addEventListener('click', async () => {
  const tamanho  = parseInt(document.getElementById('tamanho').value || '16', 10)
  const simbolos = document.getElementById('simbolos').checked

  // Requisição ao backend para gerar senha
  const res = await fetch(apiBase + `/gerar?tamanho=${tamanho}&simbolos=${simbolos}`)

  if (!res.ok) {
    alert('Erro ao gerar')
    return
  }

  const data = await res.json()
  saida.value = data.senha
})

// ============================================
// Função para copiar senha gerada
// ============================================
copiarBtn.addEventListener('click', async () => {
  if (!saida.value) {
    return alert('Ainda não gerou senha')
  }

  await navigator.clipboard.writeText(saida.value)
  alert('Senha copiada!')
})