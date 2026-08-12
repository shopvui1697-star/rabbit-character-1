"use client";

import type { UIAction } from "@/lib/types";
import { RestaurantList } from "./panels/RestaurantList";
import { RestaurantDetail } from "./panels/RestaurantDetail";
import { MovieList } from "./panels/MovieList";
import { MovieDetail } from "./panels/MovieDetail";
import { MapView } from "./panels/MapView";
import { ReviewsPanel } from "./panels/ReviewsPanel";
import { Confirmation } from "./panels/Confirmation";
import { PlanEditor } from "./panels/PlanEditor";
import { MusicPlayer } from "./panels/MusicPlayer";
import { SplitView } from "./panels/SplitView";

interface Props {
  actions: UIAction[];
}

/**
 * Declarative UI renderer — maps UIAction types from the backend to React
 * panel components. This component contains NO business logic; it is a
 * pure mapping layer.
 */
export function DynamicContent({ actions }: Props) {
  if (actions.length === 0) return null;

  return (
    <div className="flex flex-col gap-4">
      {actions.map((action, index) => (
        <ActionPanel key={`${action.action}-${index}`} action={action} />
      ))}
    </div>
  );
}

function ActionPanel({ action }: { action: UIAction }) {
  const data = action.data as Record<string, unknown>;

  switch (action.action) {
    case "SHOW_RESTAURANT_LIST":
      return <RestaurantList restaurants={data.restaurants as never} />;

    case "SHOW_RESTAURANT_DETAIL":
      return <RestaurantDetail restaurant={data.restaurant as never} />;

    case "SHOW_MOVIE_LIST":
      return <MovieList movies={data.movies as never} />;

    case "SHOW_MOVIE_DETAIL":
      return <MovieDetail movie={data.movie as never} />;

    case "SHOW_MAP":
      return (
        <MapView
          markers={data.markers as never}
          center={data.center as never}
        />
      );

    case "SHOW_REVIEWS":
      return (
        <ReviewsPanel
          restaurant_name={data.restaurant_name as string}
          average_rating={data.average_rating as number}
          reviews={data.reviews as never}
        />
      );

    case "SHOW_CONFIRMATION":
      return (
        <Confirmation
          status={data.status as never}
          title={data.title as string}
          message={data.message as string}
          details={data.details as never}
        />
      );

    case "SHOW_PLAN_EDITOR":
      return (
        <PlanEditor
          title={data.title as string}
          date={data.date as string}
          items={data.items as never}
        />
      );

    case "SHOW_MUSIC_PLAYER":
      return (
        <MusicPlayer
          track_name={data.track_name as string}
          artist={data.artist as string}
          album_art={data.album_art as string}
          duration={data.duration as string}
        />
      );

    case "SPLIT_VIEW":
      return (
        <SplitView
          left={data.left as never}
          right={data.right as never}
        />
      );

    case "CLEAR_UI":
      return null;

    default:
      return (
        <div className="p-6 text-sm text-[var(--color-text-dim)]">
          Unknown UI action: {action.action}
        </div>
      );
  }
}
