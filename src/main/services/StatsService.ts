import https from "https";
import { IncomingMessage } from "http";
import { devLog, devError } from "../logger";

interface TrackerSegment {
  attributes?: {
    playlist?: string;
  };
  stats?: Record<
    string,
    {
      value?: number;
      displayValue?: string;
      metadata?: {
        tierName?: string;
        rankName?: string;
        iconUrl?: string;
      };
    }
  >;
}

interface TrackerResponse {
  data?: {
    segments?: TrackerSegment[];
  };
}

export class StatsService {
  private readonly HEADERS = {
    "User-Agent":
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    Accept: "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    Origin: "https://tracker.gg",
    Referer: "https://tracker.gg/",
  };

  private readonly REQUEST_TIMEOUT_MS = 10000;
  private readonly MAX_RETRIES = 2;
  private readonly CACHE_TTL_MS = 60_000;
  private readonly cache = new Map<
    string,
    {
      value: { rank: string; rankIcon: string; lastUpdate: number };
      ts: number;
    }
  >();

  constructor() {}

  public async fetchAccountStats(
    riotId: string,
    gameType: "league" | "valorant",
  ) {
    devLog(`StatsService: Fetching ${gameType} stats for ${riotId}...`);
    const cacheKey = `${gameType}:${riotId}`;
    const cached = this.cache.get(cacheKey);
    if (cached && Date.now() - cached.ts < this.CACHE_TTL_MS) {
      return cached.value;
    }

    const fresh =
      gameType === "league"
        ? await this.fetchLeagueStats(riotId)
        : await this.fetchValorantStats(riotId);

    if (fresh) {
      this.cache.set(cacheKey, { value: fresh, ts: Date.now() });
      return fresh;
    }

    // Échec réseau : on conserve la dernière valeur connue (même expirée)
    // plutôt que de faire disparaître le rang déjà affiché.
    return cached?.value ?? null;
  }

  private async fetchValorantStats(riotId: string) {
    try {
      const { name, tag } = this.parseRiotId(riotId);
      const url = `https://api.tracker.gg/api/v2/valorant/standard/profile/riot/${name}%23${tag}?source=web`;

      const apiResponse = await this.httpsGetWithRetry<TrackerResponse>(
        url,
        this.HEADERS,
      );
      if (!apiResponse.data?.segments) throw new Error("Invalid response");

      const VALORANT_PLAYLISTS = [
        "competitive",
        "comp",
        "ranked_solo_5x5",
        "ranked-solo-5x5",
      ];
      const segment = this.findBestSegment(
        apiResponse.data.segments,
        VALORANT_PLAYLISTS,
      );
      const { rank, icon } = this.extractRankInfo(
        segment,
        "https://trackercdn.com/cdn/tracker.gg/valorant/icons/tiers/0.png",
      );

      devLog(`[DEV-STATS] VALORANT - ${riotId}: { rank: '${rank}' }`);

      return { rank, rankIcon: icon, lastUpdate: Date.now() };
    } catch (err) {
      const errorMsg = (err as Error).message;
      if (/HTTP (403|404|429)/.test(errorMsg)) {
        devLog(
          `Stats unavailable for ${riotId} - private, not found, or rate-limited (${errorMsg.slice(0, 12)}).`,
        );
      } else {
        devError(`Error Valorant stats ${riotId}:`, errorMsg);
      }
      return null;
    }
  }

  private async fetchLeagueStats(riotId: string) {
    try {
      const { name, tag } = this.parseRiotId(riotId);
      const url = `https://api.tracker.gg/api/v2/lol/standard/profile/riot/${name}%23${tag}`;

      const apiResponse = await this.httpsGetWithRetry<TrackerResponse>(
        url,
        this.HEADERS,
      );
      if (!apiResponse.data?.segments) throw new Error("Invalid response");

      const LEAGUE_PLAYLISTS = [
        "ranked_solo_5x5",
        "ranked-solo-5x5",
        "ranked-solo",
        "rank-solo",
      ];
      const segment = this.findBestSegment(
        apiResponse.data.segments,
        LEAGUE_PLAYLISTS,
      );
      const { rank, icon } = this.extractRankInfo(
        segment,
        "https://trackercdn.com/cdn/tracker.gg/lol/ranks/2023/icons/unranked.svg",
      );

      devLog(`[DEV-STATS] LEAGUE - ${riotId}: { rank: '${rank}' }`);

      return { rank, rankIcon: icon, lastUpdate: Date.now() };
    } catch (err) {
      const errorMsg = (err as Error).message;
      if (/HTTP (403|404|429)/.test(errorMsg)) {
        devLog(
          `Stats unavailable for ${riotId} - private, not found, or rate-limited (${errorMsg.slice(0, 12)}).`,
        );
      } else {
        devError(`Error League stats ${riotId}:`, errorMsg);
      }
      return null;
    }
  }

  private httpsGet<T>(
    url: string,
    headers: Record<string, string>,
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const req = https.get(url, { headers }, (res) => {
        let responseBody = "";
        res.on("data", (chunk) => {
          responseBody += chunk;
        });
        res.on("end", () =>
          this.handleResponse(res, responseBody, resolve, reject),
        );
      });
      req.on("error", (err) => reject(err));
      req.setTimeout(this.REQUEST_TIMEOUT_MS, () => {
        req.destroy(new Error("Request timed out"));
      });
    });
  }

  private async httpsGetWithRetry<T>(
    url: string,
    headers: Record<string, string>,
  ): Promise<T> {
    let lastErr: Error = new Error("unknown");
    for (let attempt = 0; attempt <= this.MAX_RETRIES; attempt++) {
      try {
        return await this.httpsGet<T>(url, headers);
      } catch (err) {
        lastErr = err as Error;
        // Erreurs définitives : pas de retry (privé / introuvable / rate-limit).
        if (/HTTP (403|404|429)/.test(lastErr.message)) throw lastErr;
        if (attempt < this.MAX_RETRIES) {
          await this.delay(300 * Math.pow(2, attempt));
        }
      }
    }
    throw lastErr;
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  private handleResponse<T>(
    res: IncomingMessage,
    responseBody: string,
    resolve: (val: T) => void,
    reject: (err: Error) => void,
  ) {
    if (res.statusCode !== 200) {
      return reject(new Error(`HTTP ${res.statusCode}: ${responseBody}`));
    }

    try {
      resolve(JSON.parse(responseBody) as T);
    } catch (e) {
      reject(new Error("Failed to parse JSON response"));
    }
  }

  private parseRiotId(riotId: string) {
    const parts = riotId.split("#");
    if (parts.length !== 2) {
      throw new Error("Invalid Riot ID format. Expected: Username#TAG");
    }
    return {
      name: encodeURIComponent(parts[0]),
      tag: encodeURIComponent(parts[1]),
    };
  }

  private findBestSegment(
    segments: TrackerSegment[],
    preferredPlaylists: string[],
  ) {
    let segment = segments.find(
      (s) =>
        s.attributes?.playlist &&
        preferredPlaylists.includes(s.attributes.playlist.toLowerCase()),
    );

    if (!segment) {
      segment = segments.find((s) => s.stats && (s.stats.tier || s.stats.rank));
    }

    return segment || segments[0];
  }

  private extractRankInfo(segment: TrackerSegment, defaultIcon: string) {
    const stats = segment.stats || {};
    const rankStat = stats.tier || stats.rank || {};

    const rank =
      (rankStat.metadata &&
        (rankStat.metadata.rankName || rankStat.metadata.tierName)) ||
      "Unranked";
    const icon =
      (rankStat.metadata && rankStat.metadata.iconUrl) || defaultIcon;

    return { rank, icon };
  }
}
