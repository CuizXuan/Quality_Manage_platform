<template>
  <canvas ref="canvasRef" class="digital-rain"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animationId = null
let ctx = null
const columns = []
const fontSize = 14
const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン'

class Drop {
  constructor(x, speed) {
    this.x = x
    this.y = Math.random() * -100
    this.speed = speed
    this.value = ''
    this.maxLength = Math.floor(Math.random() * 15) + 10
  }

  update(canvasHeight) {
    this.y += this.speed
    if (this.y > canvasHeight) {
      this.y = Math.random() * -100
      this.speed = Math.random() * 2 + 1
      this.maxLength = Math.floor(Math.random() * 15) + 10
    }
    this.value = ''
    for (let i = 0; i < Math.random() * this.maxLength; i++) {
      this.value += chars[Math.floor(Math.random() * chars.length)]
    }
  }

  draw(ctx) {
    ctx.fillStyle = '#0f0'
    ctx.shadowColor = '#0f0'
    ctx.shadowBlur = 10
    ctx.fillText(this.value[0] || chars[0], this.x, this.y)
    
    if (this.value.length > 1) {
      for (let i = 1; i < this.value.length; i++) {
        const alpha = 1 - (i / this.value.length)
        ctx.fillStyle = `rgba(0, 255, 136, ${alpha * 0.5})`
        ctx.fillText(this.value[i], this.x, this.y - (i * fontSize))
      }
    }
  }
}

function init(canvas) {
  const width = canvas.width = window.innerWidth
  const height = canvas.height = window.innerHeight
  ctx = canvas.getContext('2d')
  
  const columnCount = Math.floor(width / fontSize)
  columns.length = 0
  
  for (let i = 0; i < columnCount; i++) {
    columns.push(new Drop(i * fontSize, Math.random() * 2 + 1))
  }
}

function animate() {
  if (!ctx) return
  
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
  ctx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  
  columns.forEach(drop => {
    drop.update(canvasRef.value.height)
    drop.draw(ctx)
  })
  
  animationId = requestAnimationFrame(animate)
}

onMounted(() => {
  init(canvasRef.value)
  animate()
  
  window.addEventListener('resize', () => {
    init(canvasRef.value)
  })
})

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.digital-rain {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.05;
}
</style>
