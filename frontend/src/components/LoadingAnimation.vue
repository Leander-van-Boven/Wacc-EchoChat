<template>
  <div class="loader-container">
    <div class="curved-div">
      <div class="colour-magic">
        <font-awesome-icon class="fa-2x" icon="fa-solid fa-circle-notch" spin/>
      </div>
      <div class="loading">
        Loading...
      </div>
    </div>
  </div>
</template>

<!-- https://stackoverflow.com/questions/42454027/how-to-add-a-loading-icon-while-searching-vue-js-2 -->

<script>
// import {faCirclenotch} from '@/fortawesome/free-regular-svg-icons';

export default {
  name: 'LoadingAnimation',
}
</script>

<style scoped>
.loader-container {
  width: 100%;
  height: 100%;
  /*background: rgba(0,0,0,0.8);*/
  background: #fff;
  text-align: center;
  padding-top: 2rem;
}

.curved-div > * {
  display: inline-block;
}

.loading {
  text-align: center;
  padding: 1rem;
  font-size: 1.5rem;
}

.colour-magic {
  animation-name: colorMagic;
  animation-duration: 5s;
  animation-iteration-count: infinite;
  animation-delay: 0s;
}

@keyframes colorMagic {
  0% { color: rgb(179,10,10); }
  10% { color: rgb(227,132,22); }
  20% { color: rgb(164,153,7); }
  30% { color: rgb(26,171,19); }
  40% { color: rgb(19,144,177); }
  50% { color: rgb(14,16,221); }
  60% { color: rgb(27,9,98); }
  70% { color: rgb(58,11,111); }
  80% { color: rgb(126,14,129); }
  90% { color: rgb(208,19,121); }
  100% { color: rgb(198,18,18); }
}
</style>
