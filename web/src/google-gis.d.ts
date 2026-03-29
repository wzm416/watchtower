export {}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (cfg: {
            client_id: string
            callback: (resp: { credential: string }) => void
            auto_select?: boolean
          }) => void
          renderButton: (
            el: HTMLElement,
            opts: Record<string, string | boolean | number>,
          ) => void
          disableAutoSelect: () => void
        }
      }
    }
  }
}
