// Script pour supprimer tous les boutons de test vocal
(function() {
  'use strict';

  function logAllButtons() {
    console.log('🔍 Liste de tous les boutons sur la page:');
    document.querySelectorAll('button').forEach(function(btn, index) {
      console.log(`${index}: ID=${btn.id}, Title=${btn.title}, Class=${btn.className}, Text=${btn.textContent.trim()}`);
      var icon = btn.querySelector('i');
      if (icon) {
        console.log(`   Icon: ${icon.className}`);
      }
    });
  }

  function removeVoiceTestButtons() {
    console.log('🔍 Recherche et suppression des boutons de test vocal...');

    // Supprimer par ID
    var testBtn = document.getElementById('voiceTestBtn');
    if (testBtn) {
      testBtn.remove();
      console.log('✅ Supprimé voiceTestBtn par ID');
    }

    // Supprimer par titre et texte, sans toucher le vrai bouton microphone
    document.querySelectorAll('button[title="Test reconnaissance vocale"], button[title="Tester la reconnaissance vocale"], button[title*="Test reconnaissance"], button[title*="Tester la reconnaissance"], button[title*="diagnostique"], button[title*="diagnostic"], button[title*="diagnostic vocal"]').forEach(function(btn) {
      if (btn.id !== 'voiceBtn') {
        btn.remove();
        console.log('✅ Supprimé bouton par titre:', btn.title || btn.textContent.trim());
      }
    });

    // Supprimer par icône stéthoscope, clé ou rouage
    document.querySelectorAll('i.fa-stethoscope, i.fa-cog, i.fa-wrench').forEach(function(icon) {
      var target = icon.closest('button, a, div');
      if (target && target.id !== 'voiceBtn') {
        target.remove();
        console.log('✅ Supprimé bouton parent de l’icône de diagnostic:', icon.className);
      }
    });

    // Supprimer tous les boutons voice-btn non micro
    document.querySelectorAll('.voice-btn').forEach(function(btn) {
      var icon = btn.querySelector('i');
      if (btn.id !== 'voiceBtn' && (!icon || !icon.classList.contains('fa-microphone'))) {
        btn.remove();
        console.log('✅ Supprimé voice-btn non-microphone:', btn.title || btn.id || btn.textContent.trim());
      }
    });
  }

  // Exécuter immédiatement
  logAllButtons();
  removeVoiceTestButtons();

  // Observer les changements DOM pour supprimer les boutons ajoutés dynamiquement
  var observer = new MutationObserver(function(mutations) {
    var shouldRemove = false;
    mutations.forEach(function(mutation) {
      mutation.addedNodes.forEach(function(node) {
        if (node.nodeType === 1) {
          if (node.id === 'voiceTestBtn' ||
              (node.tagName === 'BUTTON' && node.title && (node.title.toLowerCase().includes('test') || node.title.toLowerCase().includes('diagnostique') || node.title.toLowerCase().includes('diagnostic')))) {
            shouldRemove = true;
          }
          // Vérifier les descendants
          if (node.querySelector && node.querySelector('#voiceTestBtn, button[title*="test"], button[title*="diagnostique"], button[title*="diagnostic"], i.fa-stethoscope, i.fa-cog, i.fa-wrench')) {
            shouldRemove = true;
          }
        }
      });
    });
    if (shouldRemove) {
      console.log('🔄 Nouveaux boutons détectés, suppression...');
      setTimeout(function() {
        logAllButtons();
        removeVoiceTestButtons();
      }, 10);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Exécuter plusieurs fois pour être sûr
  setTimeout(function() { logAllButtons(); removeVoiceTestButtons(); }, 100);
  setTimeout(function() { logAllButtons(); removeVoiceTestButtons(); }, 500);
  setTimeout(function() { logAllButtons(); removeVoiceTestButtons(); }, 1000);
  setTimeout(function() { logAllButtons(); removeVoiceTestButtons(); }, 2000);

  console.log('🛡️ Système de suppression des boutons de test vocal activé');
})();