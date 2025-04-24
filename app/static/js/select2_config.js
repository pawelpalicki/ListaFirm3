// Common Select2 configuration
const Select2Config = {
    // Podstawowa konfiguracja dla wszystkich instancji Select2
    defaultConfig: {
        width: '100%',
        theme: 'default',
        allowClear: true,
        language: {
            noResults: function() {
                return "Nie znaleziono wyników";
            },
            searching: function() {
                return "Szukam...";
            }
        },
        dropdownCssClass: "select2-dropdown--custom",
        selectionCssClass: "select2-selection--custom"
    },

    // Funkcja normalizująca tekst dla lepszego wyszukiwania
    normalizeText: function(text) {
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase();
    },

    // Inicjalizacja dla pola z placeholder
    initWithPlaceholder: function(selector, placeholder, parent = null) {
        const config = { 
            ...this.defaultConfig,
            placeholder: placeholder
        };

        if (parent) {
            config.dropdownParent = $(parent);
        }

        return $(selector).select2(config);
    },

    // Inicjalizacja dla multi-select
    initMultiSelect: function(selector, placeholder, parent = null) {
        return this.initWithPlaceholder(selector, placeholder, parent);
    },

    // Inicjalizacja zwykłego select
    // initSelect: function(selector, parent = null) {
    //     const config = { ...this.defaultConfig };

    //     if (parent) {
    //         config.dropdownParent = $(parent);
    //     }

    //     return $(selector).select2(config);
    // },

    // Inicjalizacja select z niestandardowym matcher dla polskich znaków
    initWithMatcher: function(selector, placeholder = null) {
        const self = this;

        $.fn.select2.amd.require(['select2/compat/matcher'], function(matcher) {
            const config = {
                ...self.defaultConfig,
                matcher: function(params, data) {
                    if ($.trim(params.term) === '') {
                        return data;
                    }
                    if (typeof data.text === 'undefined') {
                        return null;
                    }
                    var normalizedSearchTerm = self.normalizeText(params.term);
                    var normalizedDataText = self.normalizeText(data.text);
                    if (normalizedDataText.indexOf(normalizedSearchTerm) > -1) {
                        return data;
                    }
                    return null;
                }
            };

            if (placeholder) {
                config.placeholder = placeholder;
            }

            $(selector).select2(config);
        });
    },

    // Inicjalizacja wszystkich selektorów na stronie
    initializeAll: function() {
        // Główna strona
        if ($('#specialties').length) {
            this.initWithPlaceholder('#specialties', "Wybierz specjalność - wpisz by filtrować", $('body'));
        }

        if ($('#specialties-mobile').length) {
            this.initWithPlaceholder('#specialties-mobile', "Wybierz specjalność - wpisz by filtrować", $('#mobile-filter-overlay'));
        }

        // Formularz dodawania firmy
        if ($('#specjalnosci').length) {
            this.initMultiSelect('#specjalnosci', "Wybierz specjalności...");
        }

        if ($('#wojewodztwa').length) {
            this.initMultiSelect('#wojewodztwa', "Wybierz województwa...");
        }

        if ($('#powiaty').length) {
            this.initMultiSelect('#powiaty', "Wybierz powiaty...");
        }

        // Inicjalizacja dla typowych selectów formularza
        $('.form-select:not([data-select2-id])').each(function() {
            Select2Config.initSelect(this);
        });
    },

    // Inicjalizacja dla dynamicznie dodawanych elementów
    // initializeDynamicElement: function(container) {
    //     $(container).find('select:not([data-select2-id])').each(function() {
    //         Select2Config.initSelect(this);
    //     });
    // }
};

// Inicjalizacja po załadowaniu dokumentu
$(document).ready(function() {
    Select2Config.initializeAll();
});