<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
import FileUpload from './components/FileUpload.vue'
</script>

<template>
  <div class="app-root">
    <div class="page-title">回译助手</div>
    <FileUpload />
  </div>
</template>

<style>
html, body, #app, .app-root {
  margin: 0;
  padding: 0;
  width: 100vw;
  min-width: 0;
  min-height: 100vh;
  background: #f6f8fa;
  box-sizing: border-box;
  overflow-x: hidden;
}

.page-title {
  text-align: center;
  font-size: 2.4rem;
  color: #409EFF;
  font-weight: bold;
  margin: 32px 0 24px 0;
  letter-spacing: 2px;
}

header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}

.app-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}

h1 {
  color: #409EFF;
  margin-bottom: 30px;
}

td, th {
  white-space: pre-line;
  word-break: break-all;
  max-width: 600px;
  overflow-wrap: break-word;
  height: auto;
  vertical-align: top;
}

.main-container {
  width: 100vw;
  min-height: 100vh;
  box-sizing: border-box;
  padding: 0;
  background: #f6f8fa;
  overflow-x: hidden;
}

.upload-sections {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  margin-bottom: 32px;
  width: 100vw;
}

.upload-section {
  flex: 1 1 0;
  min-width: 320px;
  max-width: 50vw;
}

.translations-list {
  width: 100vw;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px #0001;
  padding: 24px 24px 32px 24px;
  position: relative;
  min-height: 400px;
  overflow: visible !important;
}

.full-table {
  width: 100%;
  table-layout: fixed;
  word-break: break-all;
}
</style>
