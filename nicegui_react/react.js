export default {
  template: "<div></div>",
  props: {
    bundle_url: String,
    css_urls: Array,
    react_props: Object,
    react_events: Array,
    reload_token: [String, Number],
  },
  data() {
    return {
      handle: null,
      loaded_token: null,
    };
  },
  async mounted() {
    // NOTE: wait for window.path_prefix to be available (set by NiceGUI on first tick).
    await this.$nextTick();
    this._injectCss();
    await this._loadBundle();
  },
  beforeUnmount() {
    this._unmount();
  },
  // Vue 2 compatibility (NiceGUI uses Vue 3, but keep both names harmless).
  beforeDestroy() {
    this._unmount();
  },
  watch: {
    react_props: {
      handler(value) {
        if (this.handle) this.handle.update(value, this.react_events);
      },
      deep: true,
    },
    react_events: {
      handler(value) {
        if (this.handle) this.handle.update(this.react_props, value);
      },
      deep: true,
    },
    reload_token(value) {
      // Used by dev mode to hot-reload the bundle after a rebuild.
      this.reload(value);
    },
  },
  methods: {
    _prefix() {
      return typeof window !== "undefined" && window.path_prefix ? window.path_prefix : "";
    },
    _injectCss() {
      const prefix = this._prefix();
      (this.css_urls || []).forEach((href) => {
        const full = prefix + href;
        // Idempotent: only add each stylesheet once per document.
        if (!document.querySelector(`link[data-nicegui-react="${CSS.escape(full)}"]`)) {
          const link = document.createElement("link");
          link.rel = "stylesheet";
          link.href = full;
          link.setAttribute("data-nicegui-react", full);
          document.head.appendChild(link);
        }
      });
    },
    async _loadBundle() {
      if (!this.bundle_url) return;
      const prefix = this._prefix();
      const token = this.reload_token;
      this.loaded_token = token;
      const url = prefix + this.bundle_url + (token != null ? `?v=${token}` : "");
      try {
        const module = await import(/* @vite-ignore */ url);
        if (!module || typeof module.mount !== "function") {
          console.error("nicegui-react: bundle does not export a mount() function:", url);
          return;
        }
        // Read the latest reactive values in case props changed while importing.
        this.handle = module.mount(
          this.$el,
          this.react_props || {},
          (name, data) => this.$emit(name, data),
          this.react_events || []
        );
      } catch (error) {
        console.error("nicegui-react: failed to load bundle", url, error);
      }
    },
    _unmount() {
      if (this.handle && typeof this.handle.unmount === "function") {
        try {
          this.handle.unmount();
        } catch (error) {
          console.error("nicegui-react: error while unmounting", error);
        }
      }
      this.handle = null;
    },
    async reload() {
      this._unmount();
      this._injectCss();
      await this._loadBundle();
    },
  },
};
