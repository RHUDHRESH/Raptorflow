"use client";

import { useCampaigns } from "@/lib/hooks/useCampaigns";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/custom/EmptyState";
import { Zap } from "lucide-react";
import { formatDate } from "@/lib/utils/formatters";

export default function CampaignsPage() {
  const { data: campaigns, isLoading } = useCampaigns();

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Campaigns</h1>
        <Button>Create Campaign</Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-48 bg-gray-100 rounded-lg animate-pulse"
            />
          ))}
        </div>
      ) : !campaigns || campaigns.length === 0 ? (
        <EmptyState
          title="No campaigns yet"
          description="Create your first 90-day marketing campaign"
          action={{
            label: "Create Campaign",
            onClick: () => {
              // Open create campaign modal
            },
          }}
          icon={<Zap size={40} />}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {campaigns.map((campaign) => (
            <Card key={campaign.id} className="hover:shadow-lg transition">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{campaign.title}</CardTitle>
                    <p className="text-xs text-gray-600 mt-1">
                      Week {campaign.week_number}
                    </p>
                  </div>
                  <Badge variant="outline">{campaign.status}</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  {campaign.objective}
                </p>

                {campaign.kpi_primary && (
                  <div className="mb-4 p-3 bg-gray-50 rounded-md">
                    <p className="text-xs text-gray-600 mb-1">Primary KPI</p>
                    <p className="font-semibold text-gray-900">
                      {campaign.kpi_primary}
                    </p>
                    {campaign.kpi_baseline && (
                      <p className="text-xs text-gray-600 mt-1">
                        {campaign.kpi_baseline} → {campaign.kpi_target}
                      </p>
                    )}
                  </div>
                )}

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="default"
                    className="flex-1"
                  >
                    Open
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                  >
                    Edit
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
